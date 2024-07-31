create table if not exists token
(
    id                bigint unsigned auto_increment comment '主键' primary key,
    email             varchar(64)   default ''                    not null comment '邮箱',
    type              varchar(32)   default 'openai'              not null comment 'token类型 openai, claude',
    refresh_token     varchar(255)  default ''                    not null comment '刷新token',
    access_token      varchar(2048) default ''                    not null comment '访问token 每8天更新一次',
    prefix            varchar(32)   default ''                    not null comment 'key前缀匹配,eg rd',
    assign_to         varchar(64)   default ''                    not null comment '分配给',
    remark            varchar(32)   default ''                    not null comment '备注',
    deleted           tinyint       default 0                     not null comment '是否删除 0 未删除 1 已删除',
    last_refresh_time datetime      default '1970-01-01 00:00:00' not null comment '上次刷新时间',
    expire_time       datetime      default '1970-01-01 00:00:00' not null comment '过期时间',
    create_time       datetime      default CURRENT_TIMESTAMP     not null comment '创建时间',
    update_time       datetime      default CURRENT_TIMESTAMP     not null on update CURRENT_TIMESTAMP comment '更新时间'
) comment 'token表';
create table if not exists token_relation
(
    id                bigint unsigned auto_increment comment '主键' primary key,
    token_id          bigint unsigned                            not null comment 'token id',
    user_key          varchar(128) default ''                    not null comment '使用者 key',
    share_token       varchar(64)  default ''                    not null comment '共享 token',
    deleted           tinyint      default 0                     not null comment '是否删除 0 未删除 1 已删除',
    last_refresh_time datetime     default '1970-01-01 00:00:00' not null comment '上次刷新时间',
    last_used_time    datetime     default CURRENT_TIMESTAMP     not null comment '上次使用时间',
    create_time       datetime     default CURRENT_TIMESTAMP     not null comment '创建时间',
    update_time       datetime     default CURRENT_TIMESTAMP     not null on update CURRENT_TIMESTAMP comment '更新时间'
)
    comment 'token关联表';
