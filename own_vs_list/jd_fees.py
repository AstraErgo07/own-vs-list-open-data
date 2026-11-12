"""Published JD Worldwide Open Platform category fees.

Source: the public rule page
https://jdw-rule.jd.hk/detail?ruleId=950583665543483392
(京东全球购开放平台各类目资费标准).

This is a published platform fee schedule, not a product listing.
Nothing here is scraped from a catalogue. The schedule is for JD Worldwide
(cross-border POP). A domestic JD.com POP card may differ; that is disclosed.

Operation-support service fee = category commission.
Transaction service fee = 0.90% uniform for POP merchants from 1 April 2023.
Deposits are in US dollars, by trailing GMV band, as published.
"""
from __future__ import annotations

from dataclasses import dataclass

from .published import JDW_FEE_LABEL, JDW_FEE_URL, JDW_TRANSACTION_FEE


@dataclass(frozen=True)
class JDFeeRow:
    """One published fee-schedule row."""

    first_level: str          # 一级类目, JD's own name
    first_level_en: str
    second_level: str         # 二级类目
    second_level_en: str
    third_level: str          # 三级类目, or "全部"
    third_level_en: str
    commission: float         # 运营支持服务费率
    transaction_fee: float    # 交易服务费率, uniformly 0.90%
    # Deposits in USD: GMV < 50k RMB, 50–100k, 100–300k, >=300k, brand-flagship
    deposit_usd: tuple        # five numbers
    note: str = ""

    @property
    def take_rate(self) -> float:
        """Platform 3P take on a completed sale: commission + transaction fee."""
        return self.commission + self.transaction_fee

    @property
    def label(self) -> str:
        return JDW_FEE_LABEL

    @property
    def url(self) -> str:
        return JDW_FEE_URL

    @property
    def commission_display(self) -> str:
        return (
            f"{self.commission:.2%} operation-support service fee + "
            f"{self.transaction_fee:.2%} transaction service fee "
            f"= {self.take_rate:.2%} of selling price"
        )


TX = JDW_TRANSACTION_FEE  # 0.009

# Deposit helper: (gmv<50k, 50-100k, 100-300k, >=300k, brand flagship) USD
D_STD = (2_000, 3_000, 7_000, 15_000, 7_000)
D_HIGH = (10_000, 10_000, 15_000, 15_000, 15_000)
D_BEAUTY = (10_000, 10_000, 15_000, 15_000, 5_000)
D_APPAREL = (15_000, 15_000, 15_000, 15_000, 5_000)
D_APPLIANCE_OTHER = (2_000, 3_000, 7_000, 15_000, 5_000)
D_BABY = (5_000, 5_000, 5_000, 5_000, 5_000)


# The five first-level categories used in the app, with the sub-category
# rows we actually evaluate. Names are JD's own fee-schedule names.
FEE_ROWS: dict[str, JDFeeRow] = {
    "ha_major": JDFeeRow(
        first_level="家用电器", first_level_en="Home appliances",
        second_level="大家电", second_level_en="Major appliances",
        third_level="其他三级类目",
        third_level_en="Other third-level categories (the general merchandise row; '特殊商品' is a higher-deposit exception at the same fee)",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
        note="Published fee for 大家电 other third-level categories. Special-goods rows have the same 3.00% + 0.90% and a higher deposit.",
    ),
    "ha_kitchen": JDFeeRow(
        first_level="家用电器", first_level_en="Home appliances",
        second_level="厨卫大电", second_level_en="Kitchen and bath major appliances",
        third_level="全部", third_level_en="All",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "ha_av": JDFeeRow(
        first_level="家用电器", first_level_en="Home appliances",
        second_level="视听影音", second_level_en="Audio-visual",
        third_level="其他三级类目",
        third_level_en="Other third-level categories (microphones are a higher-deposit exception at the same fee)",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "ha_commercial": JDFeeRow(
        first_level="家用电器", first_level_en="Home appliances",
        second_level="商用电器", second_level_en="Commercial appliances",
        third_level="全部", third_level_en="All",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "co_pc": JDFeeRow(
        first_level="电脑、办公", first_level_en="Computers and office",
        second_level="电脑整机", second_level_en="Complete computers",
        third_level="笔记本、台式机、服务器、笔记本配件、游戏本、平板电脑配件、一体机、特殊商品、工作站",
        third_level_en="Notebooks, desktops, servers, notebook accessories, gaming notebooks, tablet accessories, all-in-ones, special goods, workstations",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "co_tablet": JDFeeRow(
        first_level="电脑、办公", first_level_en="Computers and office",
        second_level="电脑整机", second_level_en="Complete computers",
        third_level="平板电脑", third_level_en="Tablets",
        commission=0.02, transaction_fee=TX, deposit_usd=D_STD,
        note="The published tablet row is 2.00%, not 3.00%. Transaction fee is still 0.90%.",
    ),
    "co_peripherals": JDFeeRow(
        first_level="电脑、办公", first_level_en="Computers and office",
        second_level="外设产品", second_level_en="Peripherals",
        third_level="键盘、鼠标、摄像头、移动机械硬盘、U盘、硬盘盒、手写板、鼠标垫/腕垫、插座/转换器、UPS电源、线缆、电脑工具、电脑清洁、网络仪表仪器、特殊商品、智能手写本/笔、移动固态硬盘、扩展坞",
        third_level_en="Keyboards, mice, cameras, portable drives, flash drives and the other named third-level items on this row",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "co_network": JDFeeRow(
        first_level="电脑、办公", first_level_en="Computers and office",
        second_level="网络产品", second_level_en="Network products",
        third_level="路由器、网卡、交换机、网络存储、5G/4G上网、网络盒子、网络配件、特殊商品、网线",
        third_level_en="Routers, network cards, switches, NAS, 5G/4G, network boxes, accessories, special goods, cables",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "co_office": JDFeeRow(
        first_level="电脑、办公", first_level_en="Computers and office",
        second_level="办公设备", second_level_en="Office equipment",
        third_level="传真设备、复合机、扫描仪、投影机、碎纸机、考勤机、验钞/点钞机、塑封机/塑封膜、白板、保险柜/箱、装订/封装机、投影配件、收银设备、安防监控、会议音频视频、特殊商品、条码扫描、企业离位报警器、硬盘消磁机、喷墨打印机、激光打印机",
        third_level_en="The general office-equipment row (printers as a named third-level have the same 3.00% fee and a higher deposit)",
        commission=0.03, transaction_fee=TX, deposit_usd=D_STD,
    ),
    "beauty_all": JDFeeRow(
        first_level="美妆护肤", first_level_en="Beauty and skincare",
        second_level="全部", second_level_en="All second-level categories",
        third_level="全部", third_level_en="All",
        commission=0.05, transaction_fee=TX, deposit_usd=D_BEAUTY,
        note="The published fee is uniform at 5.00% + 0.90% for every sub-level under 美妆护肤. Sub-archetypes below are price-band assumptions, not separately priced fee rows.",
    ),
    "apparel_other": JDFeeRow(
        first_level="服饰内衣", first_level_en="Apparel and underwear",
        second_level="其他二级类目", second_level_en="Other second-level categories",
        third_level="全部", third_level_en="All",
        commission=0.06, transaction_fee=TX, deposit_usd=D_APPAREL,
        note="The published merchandise fee under 服饰内衣 is 6.00% + 0.90%. The only other second-level row is 洗衣服务 (laundry service) at 0.00% commission, which is not a product and is not modelled.",
    ),
    "baby_other": JDFeeRow(
        first_level="母婴", first_level_en="Maternal and baby",
        second_level="其他二级类目", second_level_en="Other second-level categories",
        third_level="全部",
        third_level_en="All (the schedule does not list a separate formula-milk row; this is the general published bucket)",
        commission=0.02, transaction_fee=TX, deposit_usd=D_BABY,
        note="Published general 母婴 rate. Formula milk is not a separately listed fee row.",
    ),
    "baby_care": JDFeeRow(
        first_level="母婴", first_level_en="Maternal and baby",
        second_level="婴童洗护", second_level_en="Baby care and toiletries",
        third_level="全部 (婴儿驱蚊用品除外)",
        third_level_en="All except baby mosquito-repellent products, which are a 3.50% exception not modelled here",
        commission=0.02, transaction_fee=TX, deposit_usd=D_BABY,
    ),
    "baby_stroller": JDFeeRow(
        first_level="母婴", first_level_en="Maternal and baby",
        second_level="童车童床", second_level_en="Baby strollers and cots",
        third_level="全部", third_level_en="All",
        commission=0.03, transaction_fee=TX, deposit_usd=D_BABY,
    ),
    "baby_seat": JDFeeRow(
        first_level="母婴", first_level_en="Maternal and baby",
        second_level="安全座椅", second_level_en="Child safety seats",
        third_level="全部", third_level_en="All",
        commission=0.03, transaction_fee=TX, deposit_usd=D_BABY,
    ),
    "baby_clothes": JDFeeRow(
        first_level="母婴", first_level_en="Maternal and baby",
        second_level="童装", second_level_en="Children’s clothing",
        third_level="全部", third_level_en="All",
        commission=0.05, transaction_fee=TX, deposit_usd=D_BABY,
    ),
}


def take_rate(fee_id: str) -> float:
    return FEE_ROWS[fee_id].take_rate
