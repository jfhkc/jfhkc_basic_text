select * 
from 
(select t1.sumax_tk
			,t1.supply_status_tk
			,t1.sumax_part
			,t1.supply_status_part
			,row_number() over(partition by t1.sumax_part order by t1.supply_status_tk desc) as rn
from
	(select distinct 
		sumax_tk
		,supply_status_tk
		,sumax_part
		,supply_status_part	
	from `dwd_product_parts`
	where date='2025-06-04' 
		and supply_status_tk in ('批量产品','开发产品') 
		and type_simple_tk='TK'
		and sumax_part in ('CP8100'
				,'CA1039'
				,'CA1040'
				,'CR1104'
				,'BJ1120'
				,'CR1105'
				,'AK1004'
				,'107175'
				,'107228'
				,'107229'
				,'107230'
				,'107231'
				,'107232'
				,'107233'
				,'TR5001'
				,'TR9031'
				,'TR9050'
				,'TG4056'
				,'FB1104'
				,'TR9095'
				,'TG1613'
				,'TR1664'
				,'TG1858'
				,'TN1787'
				,'TG1872'
				,'FB1258'
				,'TR1862'
				,'FB1263'
				,'TR1872'
				,'TR1874'
				,'TR1886'
				,'FB1288'
				,'TR2110'
				,'TG2236'
				,'FP1015'
				,'TN2038'
				,'TN2063'
				,'TR2168'
				,'TR2201'
				,'TG2269'
				,'TN2088'
				,'TR2302'
				,'TR2303'
				,'TR2304'
				,'TN2809'
				,'TG2496'
				,'TR9098'
				,'TR2837'
				,'FB2054'
				,'TR2284'
				,'TR2900'
				,'TN9048'
				,'TN9049'
				,'TG9071'
				,'TR2355'
				,'TR2400'
				,'TR2417'
				,'TR2526'
				,'TR3035'
				,'TR3330'
				,'TR3332'
				,'TR9270')
	order by sumax_part)t1)tt1
	where tt1.rn <=5 and tt1.supply_status_tk='批量产品'

CREATE TABLE `jt_gears_dir` (
  `car_shape` varchar(150) DEFAULT NULL,
  `car_brand` varchar(20) DEFAULT NULL,
  `car_years` varchar(100) DEFAULT NULL,
  `car_year_initial` varchar(10) DEFAULT NULL,
  `jf_number` varchar(10) DEFAULT NULL,
  `teeth` varchar(120) DEFAULT NULL,
  `availableSizes` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

ManuName
Vehicle_type
Model_beginyear
Model_endyear
KW
HP
CC
LL
Cylinders
Valves
Body_style
Drive_type
Engine_type
Engine_codes
Fuel_type
Fuel_preparation
TecDoc_type
