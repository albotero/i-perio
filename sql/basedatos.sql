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
  `fecha_nacimiento` date,
  `suscripcion` text(3)
);


CREATE TABLE IF NOT EXISTS creditos (
  `transaccion` int primary key,
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
