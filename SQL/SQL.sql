
CREATE TABLE D_Cities
(
	city_id INT NOT NULL PRIMARY KEY,
	city_name VARCHAR(50)
)
--
create TABLE D_Countries
(
	country_id INT NOT NULL PRIMARY KEY,
	country_name VARCHAR(50)
)
--
CREATE TABLE D_Districts
(
	district_id INT NOT NULL PRIMARY KEY,
	district_name VARCHAR(50)
)
CREATE TABLE F_LOADS
(
load_Id  INT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
dt_start TIMESTAMP NOT NULL,
dt_end TIMESTAMP  NULL,
rows_processed INT
)


CREATE TABLE F_Emlak
(
id  INT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
load_id INT NOT NULL REFERENCES F_LOADS(load_id),
source_emlak_id INT NOT NULL,
age INT,
price INT NOT NULL,
createDate TIMESTAMP NOT NULL,
updatedDate TIMESTAMP,
mapLocation_lon NUMERIC(18,16),
mapLocation_lat NUMERIC (18,16),
city_id INT NOT NULL REFERENCES public.D_Cities(city_id),
county_id INT  NOT NULL REFERENCES public.D_Countries(country_id),
district_id  INT  NOT NULL REFERENCES public.D_Districts(district_id),
sqm_netSqm INT,
roomAndLivingRoom  VARCHAR(10),
floor_count INT,
detailDescription  VARCHAR(255),
UNIQUE(Id)
)
