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
  `id_usuario` int,
  `transaccion` text,
  `fecha_transaccion` timestamp,
  `medio_pago` text,
  `estado` text,
  `monto_cop` int,
  `gastado_cop` int
);
