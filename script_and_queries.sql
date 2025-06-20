CREATE TABLE detalle_op (
  id_pedido   INTEGER,
  id_producto INTEGER,
  nro_item    INTEGER,
  cantidad    NUMERIC
);

COPY detalle_op (id_pedido, id_producto, nro_item, cantidad)
FROM '/Users/nicolastordomar/Desktop/TPO/Datasets 2025-1/detalle_op.csv'
DELIMITER ';'
CSV HEADER;

CREATE TABLE op (
  id_pedido     INTEGER PRIMARY KEY,
  id_proveedor  INTEGER,
  fecha         DATE,
  total_sin_iva NUMERIC,
  iva           NUMERIC
);

CREATE TABLE op_raw (
  id_pedido     INTEGER PRIMARY KEY,
  id_proveedor  INTEGER,
  fecha         text,
  total_sin_iva NUMERIC,
  iva           NUMERIC
);

COPY op_raw (id_pedido, id_proveedor, fecha, total_sin_iva, iva)
FROM '/Users/nicolastordomar/Desktop/TPO/Datasets 2025-1/op.csv'
DELIMITER ';'
CSV HEADER;

INSERT INTO op (id_pedido, id_proveedor, fecha, total_sin_iva, iva)
SELECT
  id_pedido,
  id_proveedor,
  TO_DATE(fecha, 'DD/MM/YYYY'),
  total_sin_iva,
  iva
FROM op_raw;

CREATE TABLE proveedor (
  id_proveedor    INTEGER PRIMARY KEY,
  cuit_proveedor  VARCHAR(15),
  razon_social    TEXT,
  tipo_sociedad   VARCHAR(10),
  direccion       TEXT,
  activo          INTEGER,
  habilitado      INTEGER
);


copy proveedor (id_proveedor, cuit_proveedor, razon_social, tipo_sociedad, direccion, activo, habilitado)
FROM '/Users/nicolastordomar/Desktop/TPO/Datasets 2025-1/proveedor_utf8.csv'
DELIMITER ';'
CSV HEADER;

CREATE TABLE productos (
    id_producto INTEGER PRIMARY KEY,
    descripcion TEXT,
    marca TEXT,
    categoria TEXT,
    precio NUMERIC,
    stock_actual INTEGER,
    stock_futuro INTEGER
);

COPY productos(id_producto, descripcion, marca, categoria, precio, stock_actual, stock_futuro)
FROM '/Users/nicolastordomar/Desktop/TPO/Datasets 2025-1/producto_utf8.csv'
DELIMITER ';'
CSV HEADER;


CREATE TABLE telefono (
    id_proveedor INTEGER,
    codigo_area INTEGER,
    nro_telefono INTEGER,
    tipo CHAR(1)  -- F o M
);

COPY telefono(id_proveedor, codigo_area, nro_telefono, tipo)
FROM '/Users/nicolastordomar/Desktop/TPO/Datasets 2025-1/telefono.csv'
DELIMITER ';'
CSV HEADER;

-- Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos.

SELECT 
    p.id_proveedor,
    p.razon_social,
    STRING_AGG('(' || t.codigo_area || ') ' || t.nro_telefono, ', ') AS telefonos
FROM 
    proveedor p
JOIN 
    telefono t ON p.id_proveedor = t.id_proveedor
WHERE 
    p.activo = 1 AND p.habilitado = 1
GROUP BY 
    p.id_proveedor, p.razon_social;
	
-- query 2
-- Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra
-- “Tecnología” en su razón social.	
SELECT CONCAT(codigo_area, ' ', nro_telefono), razon_social 
FROM telefono t JOIN proveedor p on t.id_proveedor = p.id_proveedor
WHERE razon_social LIKE '%Tecnología%'
order by razon_social DESC

-- query 3
-- Mostrar cada teléfono junto con los datos del proveedor

SELECT CONCAT(codigo_area, ' ', nro_telefono, '|T=',tipo), p.*
FROM telefono t JOIN proveedor p on t.id_proveedor = p.id_proveedor
ORDER BY t.id_proveedor ASC

-- query4
-- Obtener todos los proveedores que tengan registrada al menos una orden de pedido
SELECT * 
FROM proveedor 
WHERE id_proveedor IN (select distinct op.id_proveedor from op) 
ORDER BY id_proveedor ASC

--query 5
-- Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
-- Es importante conocer su estado (¿el proveedor está activo?, ¿está habilitado?)
SELECT * 
FROM proveedor
WHERE id_proveedor NOT IN (select distinct op.id_proveedor from op) 
ORDER BY id_proveedor ASC

--query6
-- Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
-- monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
-- cantidad y monto en 0).

SELECT p.id_proveedor, count(distinct o.id_pedido), sum(pd.precio*(1+o.total_sin_iva*0.01)*dop.cantidad), sum(pd.precio*(1+o.iva*0.01)*dop.cantidad)  
FROM proveedor p , op o, detalle_op dop, productos pd
WHERE p.id_proveedor=o.id_proveedor and o.id_pedido = dop.id_pedido and pd.id_producto=dop.id_producto
GROUP BY p.id_proveedor
ORDER BY p.id_proveedor ASC
-- falta el caso de que me de 0. Deberiamos hacerlo con un left outer join

--query7
-- Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
-- 30-66060817-5
SELECT *
FROM op
WHERE id_proveedor = (select p.id_proveedor from proveedor p where cuit_proveedor ='30660608175' )

--query 8
-- Mostrar los productos que han sido pedido al menos 1 vez
SELECT * 
FROM productos 
WHERE id_producto IN (select distinct dop.id_producto from detalle_op dop) 

--query9
-- Listar los datos de todas las órdenes de pedido que contengan productos de la marca “COTO”
SELECT DISTINCT op.*
FROM op join detalle_op dop on op.id_pedido = dop.id_pedido 
WHERE dop.id_producto IN (select pr.id_producto from productos pr where pr.marca='COTO')
ORDER BY op.id_pedido DESC