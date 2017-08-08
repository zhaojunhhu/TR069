TR069 ACS
==============

TR069 ACS新版本正式发布，基于原ATT v3.0.0版本进行修改，已实装至服务器。

### 服务器属性

* **WEB URL**: http://80.80.80.40/itms/
* **WEB Username**: admin
* **WEB Password**: admin
* **ACS URL**: http://80.80.80.40:9090/ACS-server/ACS or http://test2.edatahome.com:9090/ACS-server/ACS

### 运营商正反向连接默认用户名密码

| **`ISP`** | **`CT`** | **`CU`** | **`standard`** |
|---------|--------|--------|--------------|
| **cpe_auth_acs_username** | **hgw** | **cpe** | **hgw** |
| **cpe_auth_acs_password** | **hgw** | **cpe** | **hgw** |
| **acs_auth_cpe_username** | **itms** | **RMS** | **itms** |
| **acs_auth_cpe_password** | **itms** | **RMS** | **itms** |

> *`standard可用于海外相关设备`*

### 更新内容

1. 电信（CT）v4.0版本分别增加GPON_4+1和EPON_4+1两种设备类型，并同时增加相对应的数据工单（与之前v4.0其他设备类型一致）。

2. 联通（CU）增加v2.0运营商版本号，包含GPON/EPON所有的设备的类型（与CT一致），并在原v1.0运营商版本的基础上增加以下工单：
**`H248_Disable`** **`H248_Enable`** **`INTERNET_PPPoE_Disable`** **`IPTV_Enable`** **`QoS_DSCP`** **`QoS_IP`**
**`SIP_Disable`** **`SIP_Enable`** **`WAN_Change`** **`WAN_Enable`** **`WAN_PPPoEIPv4v6_IPTV_IMSSIP`**
**`WAN_TR069_INTERNET_PPPoE`** **`WLAN_ADD`** **`WLAN_Enable`** **`WLAN_WEP`** **`WLAN_WPA`** 。
> *`由于CU没有明确定义IGMP取消节点，故缺少IPTV Disable相关工单；IPv6相关工单暂时只开放一个，之后会陆续添加。`*

3. 重新定义设备首次上报平台 **`0 BOOTSTRAP`** 行为：（是否修改正反向连接用户名密码以及设备管理员密码）

| **`ISP`** | **`CT`** | **`CT`** | **`CU`** | **`CU`** |
|---------|--------|--------|--------|--------|
| **VERSION** | **v3.0** | **v4.0** | **v1.0** | **v2.0** |
| **cpe_auth_acs_username** | **√** | **√** | **√** | **√** |
| **cpe_auth_acs_password** | **√** | **√** | **√** | **√** |
| **acs_auth_cpe_username** | **√** | **√** | **√** | **√** |
| **acs_auth_cpe_password** | **√** | **√** | **√** | **√** |
| **AdminPassword** | **√** | **×** | **√** | **×** |

4. 本次更新同时支持**WEB**和**Robot**两种方式的配置测试。
