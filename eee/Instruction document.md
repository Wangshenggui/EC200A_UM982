>4G_NET: 4G网络灯
    1800ms熄灭，200ms亮起->无网络(可能原因：无SIM卡、停机、欠费、SIM卡暂停服务等)
    1800ms亮起，200ms熄灭->有网络，系统可正常运行
>4G_LED: 系统状态灯(需要有网络才会有效，优先检查网络状态)
    快闪->连接CORS失败(可能原因：IP地址错误、账号或密码错误、CORS套餐过期)
    1800ms亮起，200ms熄灭->成功连接CORS服务
>BLE_LED: 蓝牙状态灯
    亮起->已连接蓝牙
    熄灭->未连接蓝牙
>RTK_STATE: RTK状态灯
    亮起->进入RTK厘米级定位模式
    熄灭->其他定位模式
>RTK_ERR: RTK故障灯
    亮起->RTK故障
    熄灭->RTK工作正常

#源代码保护声明
1.本源代码及相关文档（以下简称“源代码”）由 [贵州骞羽科技有限责任公司] （以下简称“本公司”）独立创作并享有所有知识产权，受国际及国内
    版权法的保护。未经本公司书面授权，任何个人或组织不得以任何形式复制、传播、修改、展示或利用本源代码。
2.本源代码的所有权、版权及其他相关权利均归本公司所有，任何未经授权的使用均构成对本公司权利的侵害。我们将保留追究侵权行为法律责任的权
    利，包括但不限于要求停止侵权、赔偿损失及追究刑事责任。
3.本源代码仅供授权用户在符合相关协议的前提下使用。任何尝试破解、反向工程或以其他方式获取源代码内部结构的行为均被严格禁止。
4.如需申请使用本源代码的授权，请通过以下方式与我们联系：
    电子邮箱： [1785193871@qq.com]
    联系电话： [13985821802]
    感谢您的理解与支持。

一.DRM  坐标信息
    1.坐标系代码
    2.坐标系子代码
    3.纬度偏移量
    4.纬度偏移标记
    5.经度偏移量
    6.经度偏移标记
    7.海拔偏移量
    8.参考坐标系代码
二.GBS  卫星故障检测信息
    <!-- 1.UTC 时间 -->
    2.纬度预期误差
    3.经度预期误差
    4.海拔预期误差
    5.故障卫星 ID
    6.故障卫星漏检概率
    7.故障卫星估计偏差
    8.偏差估计标准差
    9.GNSS 系统 ID
    10.GNSS 信号 ID
三.GGA  卫星定位信息
    <!-- 1.UTC 时间 -->
    <!-- 2.纬度 -->
    <!-- 3.纬度方向 -->
    <!-- 4.经度 -->
    <!-- 5.经度方向 -->
    6.RTK 状态
    7.使用中的卫星数
    8.水平精度因子
    9.海拔高度
    10.海拔高度单位
    11.地球椭球面相对大地水准面的高度
    12.地球椭球面相对大地水准面的高度单位
    13.差分数据龄期
    14.差分基站 ID
四.GGAH 同上
五.GLL  地理位置信息
    <!-- 1.纬度 -->
    <!-- 2.纬度方向 -->
    <!-- 3.经度 -->
    <!-- 4.经度方向 -->
    <!-- 5.UTC 时间 -->
    6.数据有效?
    7.定位系统模式(RTK 状态)
六.GLLH 同上
七.GNS  定位数据输出
    <!-- 1.UTC 时间 -->
    <!-- 2.纬度 -->
    <!-- 3.纬度方向 -->
    <!-- 4.经度 -->
    <!-- 5.经度方向 -->
    6.模式标识。字符长度可变，前3个字符依次为 GPS、 GLONASS、Galileo 卫星系统
    7.使用中的卫星数
    8.水平精度因子
    9.天线高
    10.地球椭球面相对大地水准面的高度，单位米
    11.差分数据龄期
    12.基站 ID
    13.导航状态指示
八.GNSH  同上
九.GST  伪距观测误差信息
    <!-- 1.UTC 时间 -->
    2.伪距、 DGNSS 改正数标准差（RMS 值）
    3.误差椭圆长半轴的标准差
    4.误差椭圆短半轴的标准差
    5.误差椭圆长半轴方向，与真北夹角
    6.纬度误差标准差
    7.经度误差标准差
    8.高程误差标准差
十.GSTH  同上
十一.THS    航向信息
    1.航向，单位为度
    2.RTK 状态
十二.RMC    卫星定位信息
    <!-- 1.UTC 时间 -->
    2.数据有效?
    <!-- 3.纬度 -->
    <!-- 4.纬度方向 -->
    <!-- 5.经度 -->
    <!-- 6.经度方向 -->
    7.地面速率，单位为节
    8.地面航向，单位为度
    9.日期
    10.磁偏角，单位：度
    11.磁偏角方向
    12.RTK 状态
    13.定位提示
十三.RMCH    同上
十四.ROT    旋转速度和方向信息
    1.旋转速率，单位：度/分
    2.数据有效?
十五.VTG    地面航向与速度信息
    1.地面航向，单位为度（以真北为基准）
    2.航向标志，固定填 T
    3.地面航向，单位为度（以磁北为基准）
    4.航向标志，固定填 M
    5.地面速率，单位为节
    6.速率单位，固定填 N
    7.地面速率，单位为 km/h
    8.速率单位，固定填 K
    9.RTK 状态
十六.VTGH   同上
十七.ZDA    日期和时间
    <!-- 1.UTC 时间 -->
    2.日
    3.月
    4.年
    5.本地时区的小时
    6.本地时区的分钟
    
