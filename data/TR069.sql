-- MySQL dump 10.13  Distrib 5.1.71, for Win32 (ia32)
--
-- Host: localhost    Database: TR069
-- ------------------------------------------------------
-- Server version	5.1.71-community

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CPE`
--

DROP TABLE IF EXISTS `CPE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CPE` (
  `CPE_ID` int(11) NOT NULL AUTO_INCREMENT,
  `SN` varchar(70) NOT NULL,
  `AUTH_TYPE` varchar(10) DEFAULT '',
  `CPE2ACS_NAME` varchar(50) DEFAULT '',
  `CPE2ACS_PASSWORD` varchar(50) DEFAULT '',
  `ACS2CPE_NAME` varchar(50) DEFAULT '',
  `ACS2CPE_PASSWORD` varchar(50) DEFAULT '',
  `CONN_RQST_URL` varchar(50) DEFAULT '',
  `CWMP_VERSION` varchar(10) DEFAULT '',
  `SOAP_INFORM_TIMEOUT` int(11) DEFAULT NULL,
  `CPE_OPERATOR` varchar(50) DEFAULT '',
  `CPE_DEVICE_TYPE` varchar(50) DEFAULT '',
  `SOFTWARE_VERSION` varchar(50) DEFAULT '',
  `HARDWARE_VERSION` varchar(50) DEFAULT '',
  `ROOT_NODE` varchar(50) DEFAULT '',
  `TIME_LAST_CONTACT` varchar(30) DEFAULT '',
  `IS_REFRESH` varchar(10) DEFAULT '',
  `TIME_SOAP_BEGIN` varchar(30) DEFAULT '',
  `TIME_SOAP_END` varchar(30) DEFAULT '',
  `SOAP_STATUS` tinyint(4) DEFAULT '0',
  `INTERFACE_VERSION` varchar(50) DEFAULT '',
  `CPE_WORKLIST_ROLLBACK` varchar(10) DEFAULT 'False',
  PRIMARY KEY (`CPE_ID`),
  UNIQUE KEY `SN_UNIQUE` (`SN`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LOG`
--

DROP TABLE IF EXISTS `LOG`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LOG` (
  `LOG_ID` int(11) NOT NULL AUTO_INCREMENT,
  `TIME_START` varchar(30) DEFAULT '',
  `TIME_FINISH` varchar(30) DEFAULT '',
  `MESSAGE` varchar(255) DEFAULT '',
  `MESSAGE2` mediumtext,
  PRIMARY KEY (`LOG_ID`),
  UNIQUE KEY `ID_UNIQUE` (`LOG_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MONITOR_RESULT`
--

DROP TABLE IF EXISTS `MONITOR_RESULT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MONITOR_RESULT` (
  `MONITOR_ID` int(11) DEFAULT NULL,
  `MONITOR_DESC` varchar(60) NOT NULL,
  `SOAP_ID` int(11) NOT NULL,
  PRIMARY KEY (`SOAP_ID`,`MONITOR_DESC`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MONITOR_RULES`
--

DROP TABLE IF EXISTS `MONITOR_RULES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MONITOR_RULES` (
  `MONITOR_ID` int(11) NOT NULL AUTO_INCREMENT,
  `MONITOR_DESC` varchar(60) DEFAULT '',
  `TYPE` varchar(20) DEFAULT '',
  `STATUS` varchar(20) DEFAULT '',
  `STATUS_DESC` mediumtext,
  `CFG` mediumtext,
  `TIME_START` varchar(30) DEFAULT '',
  `TIME_STOP` varchar(30) DEFAULT '',
  `CPE_ID` int(11) DEFAULT NULL,
  `SN` varchar(70) DEFAULT '',
  PRIMARY KEY (`MONITOR_ID`),
  UNIQUE KEY `MONITOR_DESC` (`MONITOR_DESC`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RPC`
--

DROP TABLE IF EXISTS `RPC`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RPC` (
  `RPC_ID` int(11) NOT NULL AUTO_INCREMENT,
  `RPC_NAME` char(50) DEFAULT '',
  `WORKLIST_ID` int(11) DEFAULT NULL,
  `CPE_ID` int(11) DEFAULT NULL,
  `SN` varchar(70) DEFAULT '',
  `TIME_START` varchar(30) DEFAULT '',
  `TIME_FINISH` varchar(30) DEFAULT '',
  `TIME_S1_START` varchar(30) DEFAULT '',
  `TIME_S1_FINISH` varchar(30) DEFAULT '',
  `TIME_S2_START` varchar(30) DEFAULT '',
  `TIME_S2_FINISH` varchar(30) DEFAULT '',
  `RESULT_STATUS` varchar(20) DEFAULT '',
  PRIMARY KEY (`RPC_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RPC_EX`
--

DROP TABLE IF EXISTS `RPC_EX`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `RPC_EX` (
  `RPC_ID` int(11) NOT NULL,
  `RPC_PARAMETERS` text,
  `RESULT_CONTENT` mediumtext,
  PRIMARY KEY (`RPC_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SOAP`
--

DROP TABLE IF EXISTS `SOAP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SOAP` (
  `SOAP_ID` int(11) NOT NULL AUTO_INCREMENT,
  `RPC_ID` int(11) DEFAULT NULL,
  `MSG_TYPE` varchar(50) DEFAULT '',
  `TIME_EXEC` varchar(30) DEFAULT '',
  `DIRECTION` char(4) DEFAULT '',
  `CPE_ID` int(11) DEFAULT NULL,
  `SN` varchar(70) DEFAULT '',
  `EVENT_CODE` varchar(100) DEFAULT '',
  PRIMARY KEY (`SOAP_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SOAP_EX`
--

DROP TABLE IF EXISTS `SOAP_EX`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SOAP_EX` (
  `SOAP_ID` int(11) NOT NULL,
  `CONTENT_HEAD` text,
  `HEAD_EX` text,
  `CONTENT_BODY` mediumtext,
  PRIMARY KEY (`SOAP_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WORKLIST`
--

DROP TABLE IF EXISTS `WORKLIST`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WORKLIST` (
  `WORKLIST_ID` int(11) NOT NULL AUTO_INCREMENT,
  `WORKLIST_DESC` varchar(50) DEFAULT '',
  `WORKLIST_TYPE` varchar(10) DEFAULT '',
  `WORKLIST_NAME` varchar(50) DEFAULT '',
  `STATUS` varchar(20) DEFAULT '',
  `CPE_ID` int(11) DEFAULT NULL,
  `SN` varchar(70) DEFAULT '',
  `OPERATOR` varchar(50) DEFAULT '',
  `OPERATOR_VERSION` varchar(50) DEFAULT '',
  `DOMAIN` varchar(50) DEFAULT '',
  `USER_NAME` varchar(30) DEFAULT '',
  `USER_ID` varchar(30) DEFAULT '',
  `ROLLBACK` varchar(10) DEFAULT NULL,
  `TIME_INIT` varchar(30) DEFAULT '',
  `TIME_BIND` varchar(30) DEFAULT '',
  `TIME_RESERVE` varchar(30) DEFAULT '',
  `TIME_EXEC_START` varchar(30) DEFAULT '',
  `TIME_EXEC_FINISH` varchar(30) DEFAULT '',
  `WORKLIST_GROUP` varchar(10) DEFAULT '',
  PRIMARY KEY (`WORKLIST_ID`),
  UNIQUE KEY `ID_UNIQUE` (`WORKLIST_DESC`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WORKLIST_EX`
--

DROP TABLE IF EXISTS `WORKLIST_EX`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WORKLIST_EX` (
  `WORKLIST_ID` int(11) NOT NULL,
  `PARAMETERS` mediumtext,
  `RESULT` mediumtext,
  PRIMARY KEY (`WORKLIST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WL_CONFIG`
--

DROP TABLE IF EXISTS `WL_CONFIG`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WL_CONFIG` (
  `CONFIG_ID` int(11) NOT NULL AUTO_INCREMENT,
  `ISP` varchar(50) NOT NULL,
  `VERSION` varchar(50) NOT NULL,
  `BASE_ISP` varchar(50) DEFAULT '',
  `ACS2CPE_NAME` varchar(50) DEFAULT '',
  `ACS2CPE_PASSWORD` varchar(50) DEFAULT '',
  `CPE2ACS_NAME` varchar(50) DEFAULT '',
  `CPE2ACS_PASSWORD` varchar(50) DEFAULT '',
  `EVENTCODE_MAP` text,
  PRIMARY KEY (`CONFIG_ID`),
  UNIQUE KEY `ISP` (`ISP`,`VERSION`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `WL_TEMPLATE`
--

DROP TABLE IF EXISTS `WL_TEMPLATE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `WL_TEMPLATE` (
  `TEMPLATE_ID` int(11) NOT NULL AUTO_INCREMENT,
  `ISP` varchar(50) NOT NULL,
  `VERSION` varchar(50) NOT NULL,
  `DOMAIN` varchar(50) NOT NULL,
  `METHOD` varchar(100) NOT NULL,
  `PARAMETERS` text,
  `DOC` text,
  PRIMARY KEY (`TEMPLATE_ID`),
  UNIQUE KEY `ISP` (`ISP`,`VERSION`,`DOMAIN`,`METHOD`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-04-03 16:36:18
