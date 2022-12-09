class TilkeskQuery:
    urls = []
    postal_codes = [
                    "55100",
                    "55120",
                    "55400",
                    "55420",
                    "55510",
                    "55610",
                    "55700",
                    "55800",
                    "55910"
                ]
    query = {
    "query": [
        {
            "code": "Postinumeroalue",
            "selection": {
                "filter": "item",
                "values": postal_codes
            }
        }
    ],
    "response": {
        "format": "json"
    }
    }
    file_prefix = "data"
    combined_file_prefix = "combined_data"
    years = []
    name = "data"
    def __init__(self,urls,years,file_prefix="data",postal_codes=[],query={}):
        if isinstance(years,str):
            years = [str(int(years)+i) for i,_ in enumerate(urls)]
        if len(urls) != len(years):
            raise AssertionError("The number of URLs and years must be the same.")
        self.name = file_prefix.rstrip("_")
        self.urls = urls
        self.years = years
        # Currently the query_imatra_data requires year-url pairs
        self.url_year_pair = [(year,url) for year,url in zip(years,urls)]
        self.file_prefix = file_prefix
        self.combined_file_prefix = file_prefix+str(min(years))+"-"+str(max(years))
        if postal_codes:
            self.postal_codes = postal_codes
        if query:
            self.query = query
    
    def set_years(self,years,urls=[]):
        self.years = years
        if not urls:
            urls = self.urls
        self.url_year_pair = [(year,url) for year,url in zip(years,urls)]
        self.combined_file_prefix = self.file_prefix+str(min(years))+"-"+str(max(years))
        
        
# 2013 - 2020
ikarakenne_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_1_he_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_1_he_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_1_he_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_1_he_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_1_he_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12ey.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12ey.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12ey.px",
]
#2012 - 2020, pl. 2015
koulutusrakenne_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_2_ko_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_2_ko_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_2_ko_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_2_ko_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_2_ko_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12ez.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12ez.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12ez.px",
    
]

# 2012 - 2020, pl. 2018
rahatulot_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_3_hr_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_3_hr_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_3_hr_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_3_hr_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_3_hr_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f1.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f1.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f1.px",
    
]
# 2013 - 2020
taloudet_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_4_te_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_4_te_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_4_te_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_4_te_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_4_te_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f2.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f2.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f2.px",
    
]

# 2012 - 2020, pl. 2018
talouksien_tulot_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_5_tr_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_5_tr_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_5_tr_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_5_tr_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_5_tr_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f3.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f3.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f3.px"
]
# 2013 - 2019
rakennukset_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_6_ra_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_6_ra_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_6_ra_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_6_ra_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_6_ra_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f4.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f4.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f4.px",
]
# 2012 - 2019
tyopaikat_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_7_tp_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_7_tp_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_7_tp_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_7_tp_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_7_tp_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f5.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f5.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f5.px",
]
# 2012 - 2019
paatoiminta_urls = [
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2015/paavo_8_pt_2015.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2016/paavo_8_pt_2016.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2017/paavo_8_pt_2017.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2018/paavo_8_pt_2018.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2019/paavo_8_pt_2019.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2020/paavo_pxt_12f6.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2021/paavo_pxt_12f6.px",
    "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/Postinumeroalueittainen_avoin_tieto/2022/paavo_pxt_12f6.px",
]

ikarakenneQuery = TilkeskQuery(ikarakenne_urls,years="2013",file_prefix="Imatra_ikarakenne_")
koulutusrakenneQuery = TilkeskQuery(koulutusrakenne_urls,years=["2012","2013","2014","2016","2017","2018","2019","2020"],file_prefix="Imatra_koulutusrakenne_")
rahatulotQuery = TilkeskQuery(rahatulot_urls,years=["2012","2013","2014","2015","2016","2017","2019","2020"],file_prefix="Imatra_rahatulot_")
taloudetQuery = TilkeskQuery(taloudet_urls,years="2013",file_prefix="Imatra_taloudet_")
talouksien_tulotQuery = TilkeskQuery(talouksien_tulot_urls,years=["2012","2013","2014","2015","2016","2017","2019","2020"],file_prefix="Imatra_talouksien_tulot_")
rakennuksetQuery = TilkeskQuery(rakennukset_urls,years="2013",file_prefix="Imatra_rakennukset_")
tyopaikatQuery = TilkeskQuery(tyopaikat_urls,years="2012",file_prefix="Imatra_tyopaikat_")
paatoimintaQuery = TilkeskQuery(paatoiminta_urls,years="2012",file_prefix="Imatra_paatoiminta_")

queries = [ikarakenneQuery,koulutusrakenneQuery,rahatulotQuery,taloudetQuery,talouksien_tulotQuery,rakennuksetQuery,tyopaikatQuery,paatoimintaQuery]
