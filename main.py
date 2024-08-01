import atexit
import hashlib
import json
import logging
import os
import random
import sqlite3
import string
from contextlib import closing

import pymysql
import pymysql.cursors
import requests
import utils
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from flask_cors import cross_origin

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
FUCLAUDE_BASE_URL = os.getenv("FUCLAUDE_BASE_URL", "https://demo.fuclaude.com")
SHARE_TOKEN_SITE_LIMIT = os.getenv("SHARE_TOKEN_SITE_LIMIT", "")
SITE_PASSWORD = os.getenv("SITE_PASSWORD")
if not SITE_PASSWORD:
    SITE_PASSWORD = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    logging.info(f"INIT SITE_PASSWORD: {SITE_PASSWORD}")


def execute_query(cursor, query, params=None):
    # Detect the type of connection (sqlite3 or pymysql)
    if isinstance(cursor.connection, sqlite3.Connection):
        query = query.replace("%s", "?")
    if params is None:
        params = []
    cursor.execute(query, params)


def get_db_connection():
    # 检查环境变量以决定使用哪个数据库
    if DB_HOST and DB_PORT and DB_USER and DB_PASSWORD and DB_NAME:
        # 使用 MySQL
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            logging.debug("Connected to MySQL database")
            return connection
        except pymysql.MySQLError as e:
            logging.error("Error while connecting to MySQL", e)

    # 使用 SQLite
    connection = sqlite3.connect("./data/data.db")
    connection.row_factory = sqlite3.Row

    logging.debug("Connected to SQLite database")
    return connection


def refresh_access_token(refresh_token):
    logging.info(f"refresh_access_token: {refresh_token}")
    data = {"refresh_token": refresh_token}
    resp = requests.post("https://token.oaifree.com/api/auth/refresh", data=data)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None


def get_oauth_token(share_token):
    logging.info(f"get_oauth_token: {share_token}")
    data = {"share_token": share_token}
    resp = requests.post("https://new.oaifree.com/api/auth/oauth_token", json=data)
    if resp.status_code == 200:
        return resp.json()["oauth_token"]
    return None


def register_share_token(
    unique_name, access_token, expires_in, show_conversations=False
):
    logging.info(f"register_share_token: {unique_name} {access_token} {expires_in}")
    data = {
        "unique_name": unique_name,
        "access_token": access_token,
        "expires_in": expires_in,
        "site_limit": SHARE_TOKEN_SITE_LIMIT,
        "gpt35_limit": -1,
        "gpt4_limit": -1,
        "show_conversations": show_conversations,
        # "show_userinfo": True,
        # 'temporary_chat': True,
        # 'reset_limit': True,
    }
    resp = requests.post("https://chat.oaifree.com/token/register", data=data)
    if resp.status_code == 200:
        return resp.json()["token_key"]
    return None


def get_fuclaude_oauth_token(unique_name, session_key):
    logging.info(f"get_fuclaude_oauth_token: {unique_name}, {session_key}")
    data = {"session_key": session_key, "unique_name": unique_name}
    resp = requests.post(FUCLAUDE_BASE_URL + "/manage-api/auth/oauth_token", json=data)
    if resp.status_code == 200:
        return resp.json()["oauth_token"]
    return None


def refresh_all_token():
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            # 查询上次刷新时间超过一天的token

            execute_query(
                cursor,
                "SELECT * FROM token WHERE deleted = 0 and type = 'openai' and refresh_token != '' AND last_refresh_time < %s",
                (utils.get_after_days(-9),),
            )
            tokens = cursor.fetchall()
            if not tokens:
                return []

            result = []
            # 遍历tokens，刷新access_token
            for token in tokens:
                access_token = refresh_access_token(token["refresh_token"])
                if not access_token:
                    result.append(
                        {
                            "success": False,
                            "refresh_id": token["id"],
                            "refresh_user_key": [],
                        }
                    )
                    continue

                # 更新token表的access_token和last_refresh_time
                execute_query(
                    cursor,
                    "UPDATE token SET access_token = %s, last_refresh_time = %s, expire_time = %s WHERE id = %s",
                    (
                        access_token,
                        utils.get_now(),
                        utils.get_after_days(10),
                        token["id"],
                    ),
                )
                # 查询已经分配的share_token信息
                execute_query(
                    cursor,
                    "SELECT * FROM token_relation WHERE deleted = 0 and token_id = %s",
                    (token["id"],),
                )
                token_relations = cursor.fetchall()

                refresh_user_key = []
                show_conversations = token["assign_to"] != ""
                # 遍历token_relations，重新生成share_token
                for token_relation in token_relations:
                    md5sum = hashlib.md5(
                        token_relation["user_key"].encode()
                    ).hexdigest()
                    share_token = register_share_token(
                        md5sum, access_token, 0, show_conversations
                    )
                    if not share_token:
                        refresh_user_key.append(
                            {
                                "user_key": token_relation["user_key"],
                                "success": False,
                            }
                        )
                    else:
                        # 更新token_relation表的share_token和last_refresh_time
                        execute_query(
                            cursor,
                            "UPDATE token_relation SET share_token = %s, last_refresh_time = %s WHERE id = %s",
                            (share_token, utils.get_now(), token_relation["id"]),
                        )
                        refresh_user_key.append(
                            {
                                "user_key": token_relation["user_key"],
                                "success": True,
                            }
                        )

                result.append(
                    {
                        "success": True,
                        "refresh_id": token["id"],
                        "refresh_user_key": refresh_user_key,
                    }
                )

            conn.commit()
            return result


def get_share_token_by_key(user_key):
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            # 读取数据库是否存在token，如果存在则返回token
            execute_query(
                cursor,
                "SELECT id, share_token FROM token_relation WHERE user_key = %s AND deleted = 0 LIMIT 1",
                (user_key,),
            )
            share_token_str = cursor.fetchone()
            if share_token_str:
                # 修改 last_used_time
                execute_query(
                    cursor,
                    "UPDATE token_relation SET last_used_time = %s WHERE id = %s",
                    (utils.get_now(), share_token_str["id"]),
                )
                conn.commit()
                return True, share_token_str["share_token"]

            # 根据前缀取得token
            user_key_array = user_key.split("_")
            user_key_prefix = user_key_array[0] if len(user_key_array) > 1 else ""
            # 不存在获取token表列表

            execute_query(
                cursor,
                "SELECT * FROM token WHERE deleted = 0 and type = 'openai' and prefix = %s and expire_time > %s",
                (user_key_prefix, utils.get_now()),
            )
            tokens = cursor.fetchall()
            if not tokens:
                return False, "当前没有可用的 Token"
            # 首先判断 assign_to 是否相等
            assign_token = next(
                (token for token in tokens if token["assign_to"] == user_key), None
            )
            show_conversations = True

            # 根据user_key计算hash数值取余
            md5sum = hashlib.md5(user_key.encode()).hexdigest()
            if not assign_token:
                show_conversations = False
                tokens = [token for token in tokens if token["assign_to"] == ""]
                if not tokens:
                    return False, "当前没有可用的 Token"
                hash_value = int(md5sum, 16) % len(tokens)
                assign_token = tokens[hash_value]

            # 调用接口生成新的share_token
            new_share_token = register_share_token(
                md5sum, assign_token["access_token"], 0, show_conversations
            )
            if not new_share_token:
                return False, "register share token failed"

            # 记录token_relation表
            execute_query(
                cursor,
                "INSERT INTO token_relation (user_key, share_token, token_id) VALUES (%s, %s, %s)",
                (user_key, new_share_token, assign_token["id"]),
            )
            conn.commit()
            return True, new_share_token


def get_fuclaude_token_by_key(user_key):
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            # 根据前缀取得token
            user_key_array = user_key.split("_")
            user_key_prefix = user_key_array[0] if len(user_key_array) > 1 else ""
            # 不存在获取token表列表
            execute_query(
                cursor,
                "SELECT * FROM token WHERE deleted = 0 and type = 'claude' and prefix = %s and expire_time > %s",
                (user_key_prefix, utils.get_now()),
            )
            tokens = cursor.fetchall()
            if not tokens:
                return False, "当前没有可用的 Token"
            # 首先判断 assign_to 是否相等
            assign_token = next(
                (token for token in tokens if token["assign_to"] == user_key), None
            )

            # 根据user_key计算hash数值取余
            md5sum = hashlib.md5(user_key.encode()).hexdigest()
            if not assign_token:
                tokens = [token for token in tokens if token["assign_to"] == ""]
                if not tokens:
                    return False, "当前没有可用的 Token"
                hash_value = int(md5sum, 16) % len(tokens)
                assign_token = tokens[hash_value]

            # 调用接口生成新的oauth_token
            new_share_token = get_fuclaude_oauth_token(
                md5sum, assign_token["access_token"]
            )
            if not new_share_token:
                return False, "register share token failed"

            # 记录token_relation表
            execute_query(
                cursor,
                "INSERT INTO token_relation (user_key, share_token, token_id, deleted) VALUES (%s, %s, %s, 1)",
                (user_key, '', assign_token["id"]),
            )

            conn.commit()
            return True, new_share_token


app = Flask(__name__)


def init():
    # 检查data目录是否存在
    if not os.path.exists("./data"):
        os.makedirs("./data")

    with get_db_connection() as conn:
        # 获取conn 类型，判断是否为sqlite3
        if isinstance(conn, sqlite3.Connection):
            with open("./sql/sqlite_ddl.sql", "r") as f:
                ddl_sql = f.read()
        else:
            with open("./sql/mysql_ddl.sql", "r") as f:
                ddl_sql = f.read()
        ddl_list = ddl_sql.split(";")
        with closing(conn.cursor()) as cursor:
            # 创建数据库表
            for ddl in ddl_list:
                if ddl.strip() == "":
                    continue
                cursor.execute(ddl)
            conn.commit()


def get_init_site_password():
    return SITE_PASSWORD


def saveToken(
    type, refresh_access_token_str, access_token, prefix, assign_to, email, remark
):
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            # 查询是否已经存在
            if refresh_access_token_str:
                execute_query(
                    cursor,
                    "SELECT * FROM token WHERE refresh_token = %s and deleted = 0",
                    (refresh_access_token_str,),
                )
                token = cursor.fetchone()
                if token:
                    return False, "refresh_token already exists"
            elif access_token:
                execute_query(
                    cursor,
                    "SELECT * FROM token WHERE access_token = %s and deleted = 0",
                    (access_token,),
                )
                token = cursor.fetchone()
                if token:
                    return False, "access_token already exists"

    if type == "openai" and refresh_access_token_str and not access_token:
        access_token = refresh_access_token(refresh_access_token_str)
        if not access_token:
            return False, "refresh_token is invalid"

    if type == "openai" and not email:
        email = utils.open_ai_access_token_get_email(access_token)

    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            execute_query(
                cursor,
                "INSERT INTO token (type, refresh_token, access_token, prefix, assign_to, email, remark, expire_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    type,
                    refresh_access_token_str,
                    access_token,
                    prefix,
                    assign_to,
                    email,
                    remark,
                    utils.get_after_days(10),
                ),
            )
            conn.commit()
            return True, "save token success"


@app.route("/api/share/auth/openai/login_user_key", methods=["GET"])
@cross_origin()
def get_token():
    user_key = request.args.get("user_key")
    # 如果没有user_key则默认为anonymous
    if not user_key:
        user_key = "anonymous"
    success, token = get_share_token_by_key(user_key)
    # 取得token后，调用接口获取oauth_token
    if success:
        return jsonify({"success": success, "data": get_oauth_token(token)})
    return jsonify({"success": success, "data": token})


@app.route("/api/share/auth/fuclaude/login_user_key", methods=["GET"])
@cross_origin()
def get_fuclaude_token():
    user_key = request.args.get("user_key")
    # 如果没有user_key则默认为anonymous
    if not user_key:
        user_key = "anonymous"
    success, token = get_fuclaude_token_by_key(user_key)
    # 取得token后，调用接口获取oauth_token
    return jsonify({"success": success, "data": token})


@app.route("/api/share/config/<site_password>/token", methods=["POST"])
@cross_origin()
def upload_token(site_password):
    # 校验上传密码
    db_site_password = get_init_site_password()
    if site_password != db_site_password:
        return ""
    # 获取请求json
    data = request.json
    if not data:
        return jsonify({"success": False, "data": "request data is empty"})

    type = data.get("type", "openai")
    refresh_access_token = data.get("refresh_token", "")
    access_token = data.get("access_token", "")
    prefix = data.get("prefix", "")
    assign_to = data.get("assign_to", "")
    email = data.get("email", "")
    remark = data.get("remark", "")
    if not access_token and not refresh_access_token:
        return jsonify(
            {"success": False, "data": "access_token and refresh_token is empty"}
        )
    success, message = saveToken(
        type, refresh_access_token, access_token, prefix, assign_to, email, remark
    )
    return jsonify({"success": success, "data": message})


@app.route("/api/share/config/<site_password>/token/<id>", methods=["DELETE"])
@cross_origin()
def delete_token(site_password, id):
    # 校验上传密码
    db_site_password = get_init_site_password()
    if site_password != db_site_password:
        return ""
    if not id:
        return jsonify({"success": False, "data": "id is empty"})
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            execute_query(
                cursor,
                "UPDATE token SET deleted = 1 WHERE id = %s",
                (id,),
            )
            execute_query(
                cursor,
                "UPDATE token_relation SET deleted = 1 WHERE token_id = %s",
                (id,),
            )
            conn.commit()
            return jsonify({"success": True, "data": "delete token success"})


@app.route("/api/share/config/<site_password>/token/list", methods=["GET"])
@cross_origin()
def list_token(site_password):
    # 校验上传密码
    db_site_password = get_init_site_password()
    if site_password != db_site_password:
        return ""
    with get_db_connection() as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM token WHERE deleted = 0",
            )
            tokens = cursor.fetchall()
            if isinstance(conn, sqlite3.Connection):
                tokens = [dict(row) for row in tokens]
            else:
                tokens = json.loads(json.dumps(tokens, cls=utils.DateTimeEncoder))
            return jsonify({"success": True, "data": tokens})


@app.route("/api/share/config/<site_password>/token/refresh", methods=["GET"])
@cross_origin()
def refresh_token(site_password):
    # 校验上传密码
    db_site_password = get_init_site_password()
    if site_password != db_site_password:
        return ""
    return jsonify({"success": True, "data": refresh_all_token()})


def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_all_token, "interval", days=3, id="refresh_all_token")
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    @app.before_request
    def check_scheduler():
        if not scheduler.running:
            scheduler.start()


if __name__ == "__main__":
    init()
    init_scheduler()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
