CREATE DATABASE IF NOT EXISTS iperio;
USE iperio;

CREATE TABLE IF NOT EXISTS usuarios (
  `id_usuario` int primary key not null auto_increment,
  `key` text,
  `nombres` text,
  `apellidos` text,
  `email` text,
  `creacion` timestamp,
  `telefono` text(12),
  `suscripcion` text(3),
  `email_confirmado` boolean not null default 0,
  `codigo_confirmacion_email` text
);


CREATE TABLE IF NOT EXISTS creditos (
  `transaccion` varchar(16) primary key,
  `id_usuario` int,
  `fecha_transaccion` timestamp,
  `tipo_pago` text,
  `metodo_pago` text,
  `estado` text,
  `detalle_estado` text,
  `monto` int
);


CREATE TABLE IF NOT EXISTS gastos (
  `id_usuario` int primary key,
  `gastado` int
);

CREATE TABLE IF NOT EXISTS consultorios (
  `id_usuario` int,
  `consultorio` text
);
