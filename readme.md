# 国家统计局数据抓取器

数据来自国家统计局的国家数据网站

http://data.stats.gov.cn/index.htm


## 数据抓取

可获取指定年份的所有数据 但需要分 年度、月度、季度 类型 分别抓取。输出excel文件，建议在win上进行运行，防止乱码

### 使用脚本

```shell
#获取年度数据
python main.py --type year --date 2000-2021 --dest data_year

#获取月度数据
python main.py --type M --date 2000-2021 --dest data_month
```
