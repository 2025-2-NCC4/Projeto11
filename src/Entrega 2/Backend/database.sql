create database dashboard;

use dashboard;

delete from csv where id = 1;

create table usuario(
id int auto_increment primary key,
nome varchar(50),
email varchar(50),
senha varchar(50),
cargo varchar(10)
);

create table csv(
id int auto_increment primary key,
titulo varchar(200),
caminho varchar(200),
tipoBase varchar(50),
ano int,
mes int,
idUsuario int,
foreign key (idUsuario) references usuario(id)
);
