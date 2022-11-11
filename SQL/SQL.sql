select * from  HepsiEmlak


CREATE TABLE HepsiEmlak
(
id INT NOT NULL,
age INT,
price INT NOT NULL,
createDate TIMESTAMP NOT NULL,
updatedDate TIMESTAMP,
mapLocation_lon NUMERIC(18,16),
mapLocation_lat NUMERIC (18,16),
city_id INT,
city_name VARCHAR(50),
county_id INT,
county_name VARCHAR(50),
district_id  VARCHAR(50),
district_name  VARCHAR(50),
sqm_netSqm INT,
roomAndLivingRoom  VARCHAR(10),
floor_count INT,
detailDescription  VARCHAR(255)
)
