# 地图缩放级别

### 0.问题背景

最近想把下载下来的地图切片拼接为tif图，但是下载下来是按照层级和X\Y组织的切片图片，所有我需要了解切片的组织形式，需要了解这些层级和X/Y是怎么回事？

### 1.为什么地图会切片？

- 将地图切片就是为了把世界地图变成乐高积木，想看哪块就下载哪块，让**交互式地图（拖、缩放）既快又省资源**。

### 2.为什么切片是正方形？

- 能保持一致规则网格，便于定位、计算瓦片索引
- 适配 GPU 渲染更快
- 正方形适合金字塔缩放结构（2×2）

![img](https://q5.itc.cn/images01/20241012/ce4519ce75b84ff99ecb80c9a92f543d.png)

### 3.切片的大小？

- 一般是**256*256**（绝大多数图源）
- 理论是可以是任意的

### 4.什么是缩放级别？

- 缩放级别指的是地图放大的层级。
- 在地图瓦片系统中，这个缩放级别会导致请求不同的等级下的切片

### 5.不同等级下的切片数量？

- 不同级别的切片数量就等于把整个地球切为 2<sup>n</sup> * 2<sup>n</sup> 个切片

| Zoom | 地球瓦片数                      | 每瓦片代表的区域 |
| ---- | ------------------------------- | ---------------- |
| 0    | 1×1 = 1                         | 整个地球         |
| 1    | 2×2 = 4                         | 1/4个地球        |
| 2    | 4×4 = 16                        | 1/16地球         |
| ...  | ...                             | ...              |
| 10   | 2<sup>10</sup> * 2<sup>10</sup> | 一个省或城市     |
| ...  | ...                             | ...              |
| 18   | 2<sup>18</sup> * 2<sup>18</sup> | 社区/房屋级别    |
| ...  | ...                             | ...              |
| n    | 2<sup>n</sup> * 2<sup>n</sup>   | ...              |

### 6.椭圆的地球是怎么变成平面正方形的切片的？[bing地图切片系统的介绍](https://learn.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system)

- 使用墨卡托投影，一种圆柱形投影，特点是保留了相对较小物体的形状（方形投影后还是方形），东西方向都是左右笔直，南北方向都是上下笔直，但靠近极地物体会变大
- 投影操作方式：再球心放一个灯泡，光透过地球将赤道的影子打在圆柱上，将圆柱竖向剪开展平就可以得到投影后的宽，取这个宽，截取已赤道为中心的高，就得到投影后的地球平面地图
- 为简化计算，一般使用墨卡托投影的球形形式，即将地球简化为球形再投影，会在Y方向上造成大概0.33%的缩放失真
- 由于是圆柱形，所以两极处对应的是无穷远处，所以投影后的地球实际上并没有显示整个地球，显示的最大维度是南纬85.05°~北纬85.05°

![如何绘制墨卡托投影地图? - 知乎](https://pic3.zhimg.com/v2-2cc7b055a8d25b25369a88309116740b_r.jpg?source=1940ef5c)

### 7.切片系统中x y z分别代表什么？

- x表示从左到右的列数，从左往右，x逐渐增大，值域是 0 ~ 2<sup>Z</sup> - 1 （左 → 右）
- y表示从上到下的行数，从上往下，y逐渐增大，值域是 0 ~ 2<sup>Z</sup> - 1 （上→ 下）
- z表示地图缩放等级
- 中国在45°对角线右上方，所以x比y大，所以在中国境内，数字大的是x，小的是y

```
(0,0)
┌────────▶ X+
│
│
▼ Y+
```

### 8. QGIS 里面坐标表示：

- 地理坐标系：（纬度，经度）
- 投影坐标系：（x，y）

### 9. 3857 投影坐标系和 4326 地理坐标系得换算

- 先关注经度，经度范围为【-180°，180°】
- 180°对应得就是地球得半周长，地球赤道半径为：6378137 m
- 半周长为：π * r = 3.14159 * 6378137 m = 20,037,508.342789243 m
- 所以 3857 投影坐标系下 x 的范围是 【-20,037,508.342789243 m， 20,037,508.342789243 m】
- 再关注纬度，由于是圆柱投影，所以南北极点也就是纬度为90°时，投影的位置在无穷远处。所以不可能显示到90°的，必须截断，但截断到多少度呢？
- 答案是截断成正方形，换句话说，投影后的y的范围也需要是 【-20,037,508.342789243 m， 20,037,508.342789243 m】也就是【- π * r，π * r】

### 10. 3857 投影坐标系 y 和 4326 地理坐标系纬度的换算公式？

 **Web Mercator / Mercator 投影** 的核心变换公式：

$$
y = R \cdot \ln \left( \tan\left(\frac{\pi}{4} + \frac{\varphi}{2}\right)\right)
$$

其中：

- $R$ = 地球半径（球体假设）
   在 EPSG: 3857 中采用

$$
R = 6378137 \text{ m}
$$

- $\varphi$ = 纬度（单位：弧度）

- $y$ = 投影后的北方向坐标（单位：米）

从

$$
y_{\max}=R\pi = R\ln\big(\tan(\tfrac{\pi}{4}+\tfrac{\varphi_{\max}}{2})\big)
$$

 两边除以 (R)：

$$
\pi = \ln\big(\tan(\tfrac{\pi}{4}+\tfrac{\varphi_{\max}}{2})\big)
$$

 取指数：

$$
\tan\big(\tfrac{\pi}{4}+\tfrac{\varphi_{\max}}{2}\big)=e^{\pi}
$$

 两边取反正切并解出 $\varphi_{\max}$ ：

$$
 \tfrac{\pi}{4}+\tfrac{\varphi_{\max}}{2}=\arctan(e^{\pi})
$$

 所以

$$
\varphi_{\max}=2\arctan(e^{\pi})-\tfrac{\pi}{2}.
$$

把弧度结果换成角度：

$$
\varphi_{\max,(^\circ)} = \big(2\arctan(e^{\pi})-\tfrac{\pi}{2}\big)\times\frac{180}{\pi}.
$$

数值计算得到：

$$
\varphi_{\max,(^\circ)} \approx 85.0511287798066^\circ.
$$

因此有效的纬度范围约为 $[-85.05112878^\circ, +85.05112878^\circ]$。

python公式：

```python
import math
lat_deg = 2*math.degrees(math.atan(math.exp(math.pi))) - 90.0
print(lat_deg)  # -> 85.0511287798066
```



------

### 11. 这个核心变换公式怎么推导出来的？

Mercator 投影的核心思想：

> **保持角度（形状）不变 → 局部等角（conformal projection）**

数学上，通过解微分方程：

$$
 \frac{dy}{d\varphi} = \sec \varphi = \frac{1}{\cos\varphi}
$$

因为 Mercator 必须满足经纬线保持直角，且纬度变化被放大（正割因子）。

解积分：

$$
y = R \int \sec\varphi  d\varphi
$$

而：

$$
\int \sec\varphi  d\varphi = \ln \left|\tan\left(\frac{\pi}{4} + \frac{\varphi}{2}\right)\right| + C
$$

因此得到：

$$
y = R \ln \left(\tan\left(\frac{\pi}{4} + \frac{\varphi}{2}\right)\right)
$$

这就是 Mercator 投影的由来。

来看这个函数：

$$
\tan\left(\frac{\pi}{4} + \frac{\varphi}{2}\right)
$$

当 $\varphi \to 90^\circ$ ：

$$
\frac{\pi}{4} + \frac{\pi}{2}/2 = \frac{\pi}{2}
\Rightarrow \tan\left(\frac{\pi}{2}\right) = \infty
\Rightarrow y \to +\infty
$$

即：

🌋 极点附近会被无限拉伸，无法表示！

因此 Web Mercator **人为截断**：

$$
|\varphi| \le 85.05112878^\circ
$$

也就是看到的地图只显示到大约 ±85°。

### 12. z 和地面分辨率的对应关系？

| 级别 | 地图的宽高 (像素) | 地面分辨率 (m / 像素) | 比例尺 (96 dpi 下) |
| :--- | :---------------- | :-------------------- | :----------------- |
| 1    | 512               | 78,271.5170           | 1 : 295,829,355.45 |
| 2    | 1,024             | 39,135.7585           | 1 : 147,914,677.73 |
| 3    | 2,048             | 19,567.8792           | 1 : 73,957,338.86  |
| 4    | 4,096             | 9,783.9396            | 1 : 36,978,669.43  |
| 5    | 8,192             | 4,891.9698            | 1 : 18,489,334.72  |
| 6    | 16,384            | 2,445.9849            | 1 : 9,244,667.36   |
| 7    | 32,768            | 1,222.9925            | 1 : 4,622,333.68   |
| 8    | 65,536            | 611.4962              | 1 : 2,311,166.84   |
| 9    | 131,072           | 305.7481              | 1 : 1,155,583.42   |
| 10   | 262,144           | 152.8741              | 1 : 577,791.71     |
| 11   | 524,288           | 76.4370               | 1 : 288,895.85     |
| 12   | 1,048,576         | 38.2185               | 1 : 144,447.93     |
| 13   | 2,097,152         | 19.1093               | 1 : 72,223.96      |
| 14   | 4,194,304         | 9.5546                | 1 : 36,111.98      |
| 15   | 8,388,608         | 4.7773                | 1 : 18,055.99      |
| 16   | 16,777,216        | 2.3887                | 1 : 9,028.00       |
| 17   | 33,554,432        | 1.1943                | 1 : 4,514.00       |
| 18   | 67,108,864        | **0.5972**            | 1 : 2,257.00       |
| 19   | 134,217,728       | 0.2986                | 1 : 1,128.50       |
| 20   | 268,435,456       | 0.1493                | 1 : 564.25         |
| 21   | 536,870,912       | 0.0746                | 1 : 282.12         |
| 22   | 1,073,741,824     | 0.0373                | 1 : 141.06         |
| 23   | 2,147,483,648     | 0.0187                | 1 : 70.53          |

### 13. z 和地面分辨率的换算

地面分辨率 = 每个像素在地面上代表的真实距离（米/像素）

Web Mercator 子午圈长度（赤道周长）近似采用：

$$
\text{EarthCircumference} = 2\pi R = 40075016.68557849 \text{ m}
$$

$$
 R = 6378137 \text{ m}
$$

在 zoom = 0 时，整幅地图是一个 **256×256** 的瓦片：

$$
 \text{Resolution}(z=0) = \frac{40075016.6856}{256} \approx 156543.033928 \text{ m/px}
$$

对于任意级别：

$$
{\text{Resolution}(z) = \frac{40075016.6856}{256 \cdot 2^z}}
$$

对于十八级：

$$
{\text{Resolution}(18) = \frac{40075016.6856}{256 \cdot 2^{18}} = 0.5971642834779395}
$$

- 但需要注意的是：**这个地面分辨率跟清晰度无关**，清晰度只跟卫星影像的真实分辨率有关。
- 此外，在 18 级下，在高纬度地区，**投影平面上的像素大小（视觉坐标系中）仍然是 0.597m/px** 但 **不是地球表面真实距离**！
- 事实上，纬度越高，在 3857 下测量出的距离相比真实距离越大，相对应地，测量出的面积越大。

### 14. 经纬度和切片行列x y 的转换

```python
import math

TILE_SIZE = 256  # Leaflet 默认瓦片大小

# def latlng_to_tile(lat, lng, zoom):
#     """
#     经纬度转XYZ切片坐标
#     :param lat: 纬度
#     :param lng: 经度
#     :param zoom: 缩放级别
#     :return: tile_x, tile_y
#     """
#     n = 2 ** zoom
#     x = (lng + 180.0) / 360.0 * n
#     lat_rad = math.radians(lat)
#     y = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
#     return int(x), int(y)

def latlng_to_tile(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def tile_to_latlng_bounds(tile_x, tile_y, zoom):
    """
    XYZ切片坐标转瓦片经纬度边界
    :param tile_x: 列号
    :param tile_y: 行号
    :param zoom: 缩放级别
    :return: (lat_min, lon_min, lat_max, lon_max)
    """
    n = 2 ** zoom
    lon_min = tile_x / n * 360.0 - 180.0
    lon_max = (tile_x + 1) / n * 360.0 - 180.0

    def y_to_lat(y):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))

    lat_max = y_to_lat(tile_y)
    lat_min = y_to_lat(tile_y + 1)
    return lat_min, lon_min, lat_max, lon_max

def latlng_rect_to_tiles(lat_min, lng_min, lat_max, lng_max, zoom):
    """
    经纬度矩形范围 → 覆盖的所有切片列表
    :param lat_min: 最南
    :param lng_min: 最西
    :param lat_max: 最北
    :param lng_max: 最东
    :param zoom: 缩放级别
    :return: [(tile_x, tile_y), ...]
    """
    x_min, y_max = latlng_to_tile(lat_min, lng_min, zoom)
    x_max, y_min = latlng_to_tile(lat_max, lng_max, zoom)

    tiles = []
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tiles.append((x, y))
    return tiles

# ------------------- 测试 -------------------
if __name__ == "__main__":
    lat_min, lng_min = 39.8, 116.3  # 北京附近矩形左下角
    lat_max, lng_max = 40.0, 116.5  # 北京附近矩形右上角
    zoom = 15

    tiles = latlng_rect_to_tiles(lat_min, lng_min, lat_max, lng_max, zoom)
    print(f"覆盖切片数量: {len(tiles)}")
    print("部分切片:", tiles[:10])

    # 测试单个切片边界
    print(tile_to_latlng_bounds(tiles[0][0], tiles[0][1], zoom))

```

