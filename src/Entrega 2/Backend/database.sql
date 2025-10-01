create database dashboard;

use dashboard;

create table usuario(
id int auto_increment primary key,
nome varchar(50),
email varchar(50),
senha varchar(50),
cargo varchar(10)
);