-- MySQL dump 10.14  Distrib 5.5.68-MariaDB, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: ops_manage
-- ------------------------------------------------------
-- Server version	8.0.30

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
-- Table structure for table `alarm_comment`
--

DROP TABLE IF EXISTS `alarm_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_comment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `comment_content` json NOT NULL,
  `comment_time` datetime NOT NULL,
  `identity_id` int NOT NULL,
  `pre_comment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_comment_identity_id_ea8ae6ab_fk_alarm_identity_id` (`identity_id`),
  KEY `alarm_comment_pre_comment_id_305287ba_fk_alarm_comment_id` (`pre_comment_id`),
  CONSTRAINT `alarm_comment_identity_id_ea8ae6ab_fk_alarm_identity_id` FOREIGN KEY (`identity_id`) REFERENCES `alarm_identity` (`id`),
  CONSTRAINT `alarm_comment_pre_comment_id_305287ba_fk_alarm_comment_id` FOREIGN KEY (`pre_comment_id`) REFERENCES `alarm_comment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_comment`
--

LOCK TABLES `alarm_comment` WRITE;
/*!40000 ALTER TABLE `alarm_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `alarm_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alarm_config`
--

DROP TABLE IF EXISTS `alarm_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_config` (
  `id` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `name` varchar(32) DEFAULT NULL,
  `alarm_to` json DEFAULT NULL,
  `rule_name` varchar(32) DEFAULT NULL,
  `desc` varchar(64) DEFAULT NULL,
  `alert_end` varchar(8) DEFAULT NULL,
  `alert_start` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_config_rule_name_d0b2a07a` (`rule_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_config`
--

LOCK TABLES `alarm_config` WRITE;
/*!40000 ALTER TABLE `alarm_config` DISABLE KEYS */;
INSERT INTO `alarm_config` VALUES (0,'2023-11-19 21:53:16','admin','2023-11-19 21:53:16','admin','无id告警通知','{\"sms\": [], \"ding\": [], \"email\": [{\"send_to\": [\"moran.li\"], \"timestamp\": 1700401994036, \"send_email\": \"\"}], \"phone\": [], \"wechat\": []}','','',NULL,NULL);
/*!40000 ALTER TABLE `alarm_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alarm_identity`
--

DROP TABLE IF EXISTS `alarm_identity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_identity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `identity` varchar(250) DEFAULT NULL,
  `identity_tag_kv` json DEFAULT NULL,
  `times` int DEFAULT NULL,
  `score` int DEFAULT NULL,
  `status` int NOT NULL,
  `created_at` datetime NOT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `ignore_to` datetime DEFAULT NULL,
  `handler` varchar(250) DEFAULT NULL,
  `record_ignore` tinyint(1) NOT NULL,
  `recover_cnt` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_identity_identity_d9829df7` (`identity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_identity`
--

LOCK TABLES `alarm_identity` WRITE;
/*!40000 ALTER TABLE `alarm_identity` DISABLE KEYS */;
/*!40000 ALTER TABLE `alarm_identity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alarm_rule`
--

DROP TABLE IF EXISTS `alarm_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `name` varchar(32) NOT NULL,
  `rule_keys` varchar(64) NOT NULL,
  `rule_re` varchar(64) NOT NULL,
  `rate` int NOT NULL,
  `freq` varchar(32) DEFAULT NULL,
  `desc` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_rule`
--

LOCK TABLES `alarm_rule` WRITE;
/*!40000 ALTER TABLE `alarm_rule` DISABLE KEYS */;
INSERT INTO `alarm_rule` VALUES (1,'2023-11-19 21:56:13','admin','2023-11-19 21:58:25','admin','托管prome','id,alertname','',2,'1,hour',NULL);
/*!40000 ALTER TABLE `alarm_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alarm_user`
--

DROP TABLE IF EXISTS `alarm_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alarm_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `name` varchar(32) DEFAULT NULL,
  `username` varchar(32) NOT NULL,
  `phone` varchar(24) DEFAULT NULL,
  `email` varchar(32) DEFAULT NULL,
  `desc` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_user`
--

LOCK TABLES `alarm_user` WRITE;
/*!40000 ALTER TABLE `alarm_user` DISABLE KEYS */;
INSERT INTO `alarm_user` VALUES (1,'2023-11-19 21:52:50','admin','2023-11-19 21:52:50','admin','李默然','moran.li','13524622011','moran.li@xxx.com','');
/*!40000 ALTER TABLE `alarm_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `captcha_captchastore`
--

DROP TABLE IF EXISTS `captcha_captchastore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `captcha_captchastore` (
  `id` int NOT NULL AUTO_INCREMENT,
  `challenge` varchar(32) NOT NULL,
  `response` varchar(32) NOT NULL,
  `hashkey` varchar(40) NOT NULL,
  `expiration` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hashkey` (`hashkey`)
) ENGINE=InnoDB AUTO_INCREMENT=304 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `captcha_captchastore`
--

LOCK TABLES `captcha_captchastore` WRITE;
/*!40000 ALTER TABLE `captcha_captchastore` DISABLE KEYS */;
INSERT INTO `captcha_captchastore` VALUES (303,'10*10=','100','8267a0d7e3a58655e4e698e30d12fca3449a88f6','2023-11-20 10:55:05.642503');
/*!40000 ALTER TABLE `captcha_captchastore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (21,'om_logsearch','0001_initial','2023-10-17 20:18:25.225529'),(22,'om_logsearch','0002_appconfig','2023-10-17 20:18:25.250185'),(23,'om_logsearch','0003_auto_20231016_1411','2023-10-17 20:18:25.283284'),(24,'om_logsearch','0004_auto_20231016_2304','2023-10-17 20:18:25.296898'),(25,'om_logsearch','0005_componentindex','2023-10-17 20:18:25.306586'),(26,'om_logsearch','0006_auto_20231017_1658','2023-10-17 20:18:25.326691'),(27,'om_logsearch','0007_auto_20231017_1701','2023-10-17 20:18:25.368135'),(28,'om_logsearch','0008_auto_20231018_1440','2023-10-19 11:10:26.326767'),(29,'om_logsearch','0009_auto_20231018_1618','2023-10-19 11:10:26.340845'),(30,'om_alarm','0001_initial','2023-11-19 21:34:58.720629'),(31,'om_alarm','0002_alarmidentity_record_ignore','2023-11-19 21:34:58.765861'),(32,'om_alarm','0003_auto_20231116_1450','2023-11-19 21:34:58.768594'),(33,'om_alarm','0004_auto_20231120_1530','2023-11-23 11:28:55.090042'),(34,'om_alarm','0005_auto_20231121_2030','2023-11-23 11:28:55.103985'),(35,'om_alarm','0006_alarmidentity_recover_cnt','2023-11-23 11:28:55.114533');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_appconfig`
--

DROP TABLE IF EXISTS `l_appconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_appconfig` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `app` varchar(64) NOT NULL,
  `component` varchar(32) DEFAULT NULL,
  `datasource_id` int NOT NULL,
  `isblack` varchar(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `l_appconfig_app_component_afe616f9_uniq` (`app`,`component`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_appconfig`
--

LOCK TABLES `l_appconfig` WRITE;
/*!40000 ALTER TABLE `l_appconfig` DISABLE KEYS */;
INSERT INTO `l_appconfig` VALUES (1,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-probe','yewu-app',1,'n'),(2,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-rds','yewu-app',1,'n'),(3,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-data-sync-work','yewu-app',1,'n'),(4,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-xxl-job','yewu-app',1,'n'),(5,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-auth','yewu-app',1,'n'),(6,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-meta','yewu-app',1,'n'),(7,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-data-sync-etl-es','yewu-app',1,'n'),(8,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-data-sync-etl-suc2uc','yewu-app',1,'n'),(9,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','aops-monitor','yewu-app',1,'n'),(10,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-operation-manage-server','yewu-app',1,'n'),(11,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-data-sync-etl-codis','yewu-app',1,'n'),(12,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-search-service','yewu-app',1,'n'),(13,NULL,'2023-10-17 20:36:21','sys','2023-10-17 20:36:21','sys','uc-core-service','yewu-app',1,'n'),(14,NULL,'2023-10-17 21:00:02','sys','2023-10-17 21:00:02','sys','testapp','yewu-app',1,'n'),(15,NULL,'2023-10-18 00:00:02','sys','2023-10-18 00:00:02','sys','uc-distribute-id-service','yewu-app',1,'n'),(16,NULL,'2023-10-18 00:00:02','sys','2023-10-18 00:00:02','sys','uc-operation-manage-service','yewu-app',1,'n'),(17,NULL,'2023-10-18 18:00:02','sys','2023-10-18 18:00:02','sys','xingnengceshi','yewu-app',1,'n'),(18,NULL,'2023-10-31 21:00:02','sys','2023-10-31 21:00:02','sys','testjava','yewu-app',1,'n'),(19,NULL,'2023-11-02 00:00:02','sys','2023-11-02 00:00:02','sys','uc-data-sync-work-suc2uc','yewu-app',1,'n'),(20,NULL,'2023-11-02 00:00:02','sys','2023-11-02 00:00:02','sys','uc-data-sync-work-es','yewu-app',1,'n'),(21,NULL,'2023-11-09 21:00:03','sys','2023-11-09 21:00:03','sys','aops-ms','yewu-app',1,'n');
/*!40000 ALTER TABLE `l_appconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_apppass`
--

DROP TABLE IF EXISTS `l_apppass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_apppass` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `component` varchar(32) DEFAULT NULL,
  `app` varchar(128) NOT NULL,
  `uri` varchar(64) DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `note` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_apppass`
--

LOCK TABLES `l_apppass` WRITE;
/*!40000 ALTER TABLE `l_apppass` DISABLE KEYS */;
/*!40000 ALTER TABLE `l_apppass` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_component`
--

DROP TABLE IF EXISTS `l_component`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_component` (
  `id` int NOT NULL AUTO_INCREMENT,
  `component` varchar(32) DEFAULT NULL,
  `index_str` varchar(128) NOT NULL,
  `time_field` varchar(16) DEFAULT NULL,
  `field_type` varchar(16) DEFAULT NULL,
  `source` varchar(32) NOT NULL,
  `created_at` datetime,
  `created_by` varchar(32),
  `name` varchar(64) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32),
  `datasource_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `l_component_datasource_id_component_f284399e_uniq` (`datasource_id`,`component`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_component`
--

LOCK TABLES `l_component` WRITE;
/*!40000 ALTER TABLE `l_component` DISABLE KEYS */;
INSERT INTO `l_component` VALUES (1,'yewu-app','aops-applog-*','@timestamp','applog','es','2023-10-17 20:34:59','sys',NULL,'2023-10-17 20:34:59','sys',1),(2,'yewu-apisix','aops-apisix-apisix-*','@timestamp','nginxlog','es','2023-10-17 20:35:15','sys',NULL,'2023-10-17 20:35:15','sys',1),(3,'aops-apisix','aops-apisix-filelog-*','@timestamp','nginxlog','es','2023-10-17 20:35:26','sys',NULL,'2023-10-17 20:35:26','sys',1),(4,'aops-nginx','aops-nginx-nginx-*','@timestamp','nginxlog','es','2023-10-17 20:35:37','sys',NULL,'2023-10-17 20:35:37','sys',1),(5,'yewu-tengine','aops-tengine-tengine-*','@timestamp','nginxlog','es','2023-10-17 20:35:53','sys',NULL,'2023-10-17 20:35:53','sys',1);
/*!40000 ALTER TABLE `l_component` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_datasource`
--

DROP TABLE IF EXISTS `l_datasource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_datasource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `source` varchar(32) NOT NULL,
  `host` varchar(128) DEFAULT NULL,
  `username` varchar(128) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `project_name` varchar(128) DEFAULT NULL,
  `logstore` varchar(128) DEFAULT NULL,
  `region` varchar(128) DEFAULT NULL,
  `alisecret` varchar(128) DEFAULT NULL,
  `alikey` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_datasource`
--

LOCK TABLES `l_datasource` WRITE;
/*!40000 ALTER TABLE `l_datasource` DISABLE KEYS */;
INSERT INTO `l_datasource` VALUES (1,'托管平台Es','2023-10-17 20:33:51','sys','2023-10-17 20:33:51','admin','es','172.30.14.49:9113','aops','xxx','','','','','');
/*!40000 ALTER TABLE `l_datasource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_gateconfig`
--

DROP TABLE IF EXISTS `l_gateconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_gateconfig` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `domain` varchar(128) NOT NULL,
  `component` varchar(32) DEFAULT NULL,
  `datasource_id` int NOT NULL,
  `isblack` varchar(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `l_gateconfig_domain_component_38027860_uniq` (`domain`,`component`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_gateconfig`
--

LOCK TABLES `l_gateconfig` WRITE;
/*!40000 ALTER TABLE `l_gateconfig` DISABLE KEYS */;
INSERT INTO `l_gateconfig` VALUES (1,NULL,'2023-10-17 20:36:14','sys','2023-10-17 20:36:14','sys','support.changyan.com','yewu-tengine',1,'n'),(2,NULL,'2023-10-17 20:36:14','sys','2023-10-17 20:36:14','sys','support.changyan.com','yewu-apisix',1,'n'),(3,NULL,'2023-10-26 18:00:02','sys','2023-10-26 18:00:02','sys','ebg.appcloud.xxx.com','aops-apisix',1,'n');
/*!40000 ALTER TABLE `l_gateconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `l_gatepass`
--

DROP TABLE IF EXISTS `l_gatepass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `l_gatepass` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `component` varchar(32) DEFAULT NULL,
  `domain` varchar(128) NOT NULL,
  `uri` varchar(64) DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `note` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `l_gatepass`
--

LOCK TABLES `l_gatepass` WRITE;
/*!40000 ALTER TABLE `l_gatepass` DISABLE KEYS */;
INSERT INTO `l_gatepass` VALUES (1,NULL,'2023-10-26 18:46:35','sys','2023-10-26 18:46:35','sys','yewu-apisix','support.changyan.com','/*.png',NULL,''),(2,NULL,'2023-10-26 18:46:46','sys','2023-10-26 18:46:47','sys','yewu-apisix','support.changyan.com','/*.css',NULL,''),(3,NULL,'2023-10-26 18:47:01','sys','2023-10-26 18:47:01','sys','yewu-apisix','support.changyan.com','/*.jpg',NULL,'');
/*!40000 ALTER TABLE `l_gatepass` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_dept`
--

DROP TABLE IF EXISTS `om_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_dept` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `description` varchar(16) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `order_num` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_dept_name_2b85b417` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_dept`
--

LOCK TABLES `om_dept` WRITE;
/*!40000 ALTER TABLE `om_dept` DISABLE KEYS */;
INSERT INTO `om_dept` VALUES (1,'运维部','2022-11-17 11:06:23.263457','sys','2022-11-17 11:06:23.277786','zengxin.li',NULL,NULL,0),(9,'开发部','2022-11-17 11:10:42.520737','sys','2022-11-17 11:10:42.530989','zengxin.li',NULL,NULL,0),(10,'测试部','2022-11-17 13:56:23.129717','sys','2022-11-17 13:56:23.140477','zengxin.li',NULL,NULL,255),(11,'技术支持','2022-11-17 14:05:09.272650','sys','2022-11-17 14:05:09.284398','zengxin.li',NULL,1,255),(12,'运维开发','2022-11-17 14:05:40.665001','sys','2022-11-17 14:05:40.675476','zengxin.li',NULL,1,255),(13,'技术运维','2022-11-17 14:05:49.555269','sys','2022-11-17 14:05:49.566485','zengxin.li',NULL,1,255);
/*!40000 ALTER TABLE `om_dept` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_dept_role`
--

DROP TABLE IF EXISTS `om_dept_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_dept_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_dept_role_name_07a04efc` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_dept_role`
--

LOCK TABLES `om_dept_role` WRITE;
/*!40000 ALTER TABLE `om_dept_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `om_dept_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_resource`
--

DROP TABLE IF EXISTS `om_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_resource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `icon` varchar(128) DEFAULT NULL,
  `is_show` tinyint(1) NOT NULL,
  `keepalive` tinyint(1) NOT NULL,
  `order_num` int DEFAULT NULL,
  `perms` varchar(256) DEFAULT NULL,
  `router` varchar(256) DEFAULT NULL,
  `type` int NOT NULL,
  `view_path` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_resource_name_8b2f074b` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_resource`
--

LOCK TABLES `om_resource` WRITE;
/*!40000 ALTER TABLE `om_resource` DISABLE KEYS */;
INSERT INTO `om_resource` VALUES (1,'系统','2020-08-28 10:09:26.000000',NULL,'2022-11-23 10:23:54.959628','zengxin.li',NULL,'icon-shezhi',1,1,255,NULL,'/sys',0,NULL),(3,'权限管理','2020-08-01 00:00:00.000000',NULL,'2021-12-08 14:52:50.000000',NULL,1,'icon-quanxian',1,1,0,NULL,'/sys/permssion',0,''),(4,'用户列表','2020-08-08 00:00:00.000000',NULL,'2021-12-08 14:53:35.000000',NULL,3,'icon-yonghu',1,1,0,NULL,'/sys/permssion/user',1,'views/system/permission/user'),(5,'新增','2020-08-15 00:00:00.000000',NULL,'2020-09-11 06:11:52.000000',NULL,4,NULL,1,1,0,'sys:user:add',NULL,2,NULL),(6,'删除','2020-08-15 00:00:00.000000',NULL,'2020-09-11 06:13:03.000000',NULL,4,NULL,1,1,0,'sys:user:delete',NULL,2,NULL),(7,'菜单列表','2020-08-08 00:00:00.000000',NULL,'2021-12-08 15:05:56.000000',NULL,3,'icon-tiaoxingtu',1,1,0,NULL,'/sys/permssion/menu',1,'views/system/permission/menu'),(8,'新增','2020-08-15 00:00:00.000000',NULL,'2020-08-15 00:00:00.000000',NULL,7,NULL,0,1,0,'sys:menu:add',NULL,2,NULL),(9,'删除','2020-08-15 00:00:00.000000',NULL,'2020-08-15 00:00:00.000000',NULL,7,NULL,1,1,0,'sys:menu:delete',NULL,2,NULL),(10,'查询','2020-09-02 08:22:27.000000',NULL,'2023-10-18 09:53:55.227636','admin',7,NULL,1,1,0,'sys:menu:list',NULL,2,NULL),(17,'测试','2020-09-04 06:26:36.000000',NULL,'2020-09-04 07:13:30.000000',NULL,16,'',1,1,0,'sys:menu:list,sys:menu:update,sys:menu:info,sys:menu:add','',2,''),(19,'修改','2020-09-04 08:08:53.000000',NULL,'2020-09-04 08:08:53.000000',NULL,7,'',1,1,0,'sys:menu:update','',2,''),(20,'部门移动排序','2021-04-12 04:28:03.000000',NULL,'2021-04-20 10:18:22.000000',NULL,4,NULL,1,1,255,'sys:dept:move',NULL,2,NULL),(23,'角色列表','2020-09-04 09:41:43.000000',NULL,'2021-12-08 15:05:56.000000',NULL,3,'icon-jiaosequanxian',1,1,0,'','/sys/permission/role',1,'views/system/permission/role'),(25,'删除','2020-09-07 02:44:27.000000',NULL,'2020-09-07 08:51:18.000000',NULL,23,'',1,1,0,'sys:role:delete','',2,''),(28,'新增','2020-09-07 07:08:18.000000',NULL,'2020-09-14 10:26:58.000000',NULL,23,'',1,1,0,'sys:role:add','',2,''),(29,'修改','2020-09-07 08:51:48.000000',NULL,'2020-09-07 08:51:58.000000',NULL,23,'',1,1,0,'sys:role:update','',2,''),(32,'查询','2020-09-07 10:39:50.000000',NULL,'2020-09-09 06:34:13.000000',NULL,23,'',1,1,0,'sys:role:list,sys:role:info','',2,''),(35,'更新','2020-09-10 05:09:31.000000',NULL,'2020-09-10 05:09:31.000000',NULL,4,'',1,1,0,'sys:user:update','',2,''),(36,'部门转移','2020-09-10 08:02:29.000000',NULL,'2020-09-10 08:02:40.000000',NULL,4,'',1,1,0,'sys:dept:transfer','',2,''),(39,'部门新增','2020-09-11 06:12:14.000000',NULL,'2020-09-11 06:12:14.000000',NULL,4,'',1,1,0,'sys:dept:add','',2,''),(40,'部门删除','2020-09-11 06:13:23.000000',NULL,'2020-09-11 06:13:23.000000',NULL,4,'',1,1,0,'sys:dept:delete','',2,''),(41,'部门更新','2020-09-11 06:29:52.000000',NULL,'2020-09-11 06:29:52.000000',NULL,4,'',1,1,0,'sys:dept:update','',2,''),(42,'用户查询','2023-10-11 15:38:02.371348','sys','2023-10-11 19:52:09.492623','admin',4,NULL,1,1,255,'sys:user:list',NULL,2,NULL),(43,'日志管理','2023-10-17 20:25:50.801310','sys','2023-10-17 20:25:50.811111','admin',1,'ziyuan',1,1,255,NULL,'/sys/logmanage',0,NULL),(44,'日志源','2023-10-17 20:26:47.667216','sys','2023-10-17 20:26:47.677012','admin',43,'',1,1,255,NULL,'/sys/logmanage/source',1,'views/log/source'),(45,'通用新增','2023-10-17 20:27:18.166599','sys','2023-10-18 13:49:35.017456','admin',43,NULL,1,1,255,'log:source:add',NULL,2,NULL),(46,'查看','2023-10-17 20:28:08.983699','sys','2023-10-17 20:28:41.591545','admin',44,NULL,1,1,255,'log:source:list',NULL,2,NULL),(47,'通用更新','2023-10-17 20:28:33.777979','sys','2023-10-18 13:49:41.435919','admin',43,NULL,1,1,255,'log:source:update',NULL,2,NULL),(48,'通用删除','2023-10-17 20:29:02.826427','sys','2023-10-18 13:49:48.434415','admin',43,NULL,1,1,255,'log:source:delete',NULL,2,NULL),(49,'网关配置','2023-10-17 20:29:34.163804','sys','2023-10-17 20:29:34.173014','admin',43,'',1,1,255,NULL,'/sys/logmanage/gateconfig',1,'views/log/gateconfig'),(50,'app配置','2023-10-17 20:29:58.915251','sys','2023-10-17 20:30:20.322299','admin',43,'',1,1,255,NULL,'/sys/logmanage/appconfig',1,'views/log/appconfig'),(51,'组件管理','2023-10-17 20:30:50.013418','sys','2023-10-17 20:30:50.025994','admin',43,'',1,1,255,NULL,'/sys/logmanage/component',1,'views/log/component'),(52,'查看','2023-10-17 20:31:20.023946','sys','2023-10-17 20:31:20.033409','admin',51,NULL,1,1,255,'log:component:list',NULL,2,NULL),(53,'查看','2023-10-17 20:31:38.120088','sys','2023-10-17 20:31:38.130317','admin',50,NULL,1,1,255,'log:appconfig:list',NULL,2,NULL),(54,'查看','2023-10-17 20:31:57.710898','sys','2023-10-17 20:31:57.719849','admin',49,NULL,1,1,255,'log:gateconfig:list',NULL,2,NULL),(55,'改密','2023-10-18 10:12:52.652627','sys','2023-10-18 10:12:52.661617','admin',4,NULL,1,1,255,'sys:user:password',NULL,2,NULL),(56,'网关过滤项','2023-10-19 11:02:29.700226','sys','2023-10-26 18:45:41.585317','admin',43,'',1,1,255,NULL,'/sys/logmanage/gatepass',1,'views/log/gatepass'),(57,'应用日志过滤','2023-10-19 11:02:48.179220','sys','2023-10-19 11:02:48.187801','admin',43,'',1,1,255,NULL,'/sys/logmanage/apppass',1,'views/log/apppass'),(58,'查看','2023-10-19 11:03:18.659399','sys','2023-10-19 11:03:18.667433','admin',56,NULL,1,1,255,'log:apppass:list',NULL,2,NULL),(59,'新增','2023-10-19 11:03:35.128716','sys','2023-10-19 11:03:35.138060','admin',56,NULL,1,1,255,'log:gatepass:add',NULL,2,NULL),(60,'更新','2023-10-19 11:03:51.739152','sys','2023-10-19 11:03:51.747559','admin',56,NULL,1,1,255,'log:gatepass:update',NULL,2,NULL),(61,'删除','2023-10-19 11:04:37.303739','sys','2023-10-19 11:04:37.311943','admin',56,NULL,1,1,255,'log:gatepass:delete',NULL,2,NULL),(62,'查看','2023-10-19 11:08:46.958244','sys','2023-10-19 11:08:46.967069','admin',57,NULL,1,1,255,'log:apppass:list',NULL,2,NULL),(63,'新增','2023-10-19 11:09:12.118867','sys','2023-10-19 11:09:12.127076','admin',57,NULL,1,1,255,'log:apppass:add',NULL,2,NULL),(64,'更新','2023-10-19 11:09:25.307171','sys','2023-10-19 11:09:25.315228','admin',57,NULL,1,1,255,'log:apppass:update',NULL,2,NULL),(65,'删除','2023-10-19 11:09:38.922970','sys','2023-10-19 11:09:38.930955','admin',57,NULL,1,1,255,'log:apppass:delete',NULL,2,NULL);
/*!40000 ALTER TABLE `om_resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_resource_role`
--

DROP TABLE IF EXISTS `om_resource_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_resource_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `permissions` int NOT NULL,
  `menu_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_resource_role_name_c12c5622` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=168 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_resource_role`
--

LOCK TABLES `om_resource_role` WRITE;
/*!40000 ALTER TABLE `om_resource_role` DISABLE KEYS */;
INSERT INTO `om_resource_role` VALUES (83,NULL,'2022-11-18 17:54:24.087340','sys','2022-11-18 17:54:24.088469','sys',1,0,1),(84,NULL,'2022-11-18 17:54:24.087367','sys','2022-11-18 17:54:24.088496','sys',1,0,3),(85,NULL,'2022-11-18 17:54:24.087379','sys','2022-11-18 17:54:24.088518','sys',1,0,4),(86,NULL,'2022-11-18 17:54:24.087389','sys','2022-11-18 17:54:24.088539','sys',1,0,5),(87,NULL,'2022-11-18 17:54:24.087399','sys','2022-11-18 17:54:24.088560','sys',1,0,6),(88,NULL,'2022-11-18 17:54:24.087409','sys','2022-11-18 17:54:24.088581','sys',1,0,7),(89,NULL,'2022-11-18 17:54:24.087419','sys','2022-11-18 17:54:24.088601','sys',1,0,8),(90,NULL,'2022-11-18 17:54:24.087428','sys','2022-11-18 17:54:24.088627','sys',1,0,9),(91,NULL,'2022-11-18 17:54:24.087438','sys','2022-11-18 17:54:24.088674','sys',1,0,10),(92,NULL,'2022-11-18 17:54:24.087448','sys','2022-11-18 17:54:24.088706','sys',1,0,19),(93,NULL,'2022-11-18 17:54:24.087458','sys','2022-11-18 17:54:24.088727','sys',1,0,20),(94,NULL,'2022-11-18 17:54:24.087467','sys','2022-11-18 17:54:24.088748','sys',1,0,23),(95,NULL,'2022-11-18 17:54:24.087477','sys','2022-11-18 17:54:24.088768','sys',1,0,25),(97,NULL,'2022-11-18 17:54:24.087496','sys','2022-11-18 17:54:24.088840','sys',1,0,28),(98,NULL,'2022-11-18 17:54:24.087505','sys','2022-11-18 17:54:24.088868','sys',1,0,29),(99,NULL,'2022-11-18 17:54:24.087515','sys','2022-11-18 17:54:24.088889','sys',1,0,32),(103,NULL,'2022-11-18 17:54:24.087553','sys','2022-11-18 17:54:24.088972','sys',1,0,36),(105,NULL,'2022-11-18 17:54:24.087572','sys','2022-11-18 17:54:24.089013','sys',1,0,39),(106,NULL,'2022-11-18 17:54:24.087582','sys','2022-11-18 17:54:24.089034','sys',1,0,40),(107,NULL,'2022-11-18 17:54:24.087591','sys','2022-11-18 17:54:24.089054','sys',1,0,41),(123,NULL,'2022-11-30 14:13:26.951352','sys','2022-11-30 14:13:26.952141','sys',1,0,35),(144,NULL,'2023-10-11 15:38:02.381523','sys','2023-10-11 15:38:02.381711','sys',1,0,42),(145,NULL,'2023-10-17 20:25:50.814049','sys','2023-10-17 20:25:50.814249','sys',1,0,43),(146,NULL,'2023-10-17 20:26:47.680779','sys','2023-10-17 20:26:47.681004','sys',1,0,44),(147,NULL,'2023-10-17 20:27:18.179731','sys','2023-10-17 20:27:18.180055','sys',1,0,45),(148,NULL,'2023-10-17 20:28:08.995342','sys','2023-10-17 20:28:08.995528','sys',1,0,46),(149,NULL,'2023-10-17 20:28:33.790719','sys','2023-10-17 20:28:33.790984','sys',1,0,47),(150,NULL,'2023-10-17 20:29:02.838515','sys','2023-10-17 20:29:02.838713','sys',1,0,48),(151,NULL,'2023-10-17 20:29:34.175406','sys','2023-10-17 20:29:34.175578','sys',1,0,49),(152,NULL,'2023-10-17 20:29:58.929067','sys','2023-10-17 20:29:58.929291','sys',1,0,50),(153,NULL,'2023-10-17 20:30:50.031272','sys','2023-10-17 20:30:50.031536','sys',1,0,51),(154,NULL,'2023-10-17 20:31:20.035625','sys','2023-10-17 20:31:20.035806','sys',1,0,52),(155,NULL,'2023-10-17 20:31:38.133346','sys','2023-10-17 20:31:38.133592','sys',1,0,53),(156,NULL,'2023-10-17 20:31:57.721931','sys','2023-10-17 20:31:57.722107','sys',1,0,54),(157,NULL,'2023-10-18 10:12:52.663896','sys','2023-10-18 10:12:52.664095','sys',1,0,55),(158,NULL,'2023-10-19 11:02:29.716209','sys','2023-10-19 11:02:29.716410','sys',1,0,56),(159,NULL,'2023-10-19 11:02:48.189657','sys','2023-10-19 11:02:48.189826','sys',1,0,57),(160,NULL,'2023-10-19 11:03:18.669263','sys','2023-10-19 11:03:18.669426','sys',1,0,58),(161,NULL,'2023-10-19 11:03:35.140844','sys','2023-10-19 11:03:35.141043','sys',1,0,59),(162,NULL,'2023-10-19 11:03:51.749567','sys','2023-10-19 11:03:51.749741','sys',1,0,60),(163,NULL,'2023-10-19 11:04:37.313928','sys','2023-10-19 11:04:37.314110','sys',1,0,61),(164,NULL,'2023-10-19 11:08:46.969170','sys','2023-10-19 11:08:46.969353','sys',1,0,62),(165,NULL,'2023-10-19 11:09:12.129227','sys','2023-10-19 11:09:12.129397','sys',1,0,63),(166,NULL,'2023-10-19 11:09:25.317018','sys','2023-10-19 11:09:25.317190','sys',1,0,64),(167,NULL,'2023-10-19 11:09:38.932705','sys','2023-10-19 11:09:38.932874','sys',1,0,65);
/*!40000 ALTER TABLE `om_resource_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_role`
--

DROP TABLE IF EXISTS `om_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_role_name_256ced30` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_role`
--

LOCK TABLES `om_role` WRITE;
/*!40000 ALTER TABLE `om_role` DISABLE KEYS */;
INSERT INTO `om_role` VALUES (1,'#超级管理员#','2022-11-18 15:40:06.754241','sys','2023-10-11 14:52:19.034203','admin',NULL);
/*!40000 ALTER TABLE `om_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_user`
--

DROP TABLE IF EXISTS `om_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `realname` varchar(128) DEFAULT NULL,
  `department_id` int NOT NULL,
  `email` varchar(128) DEFAULT NULL,
  `head_img` varchar(2048) DEFAULT NULL,
  `phone` varchar(128) DEFAULT NULL,
  `remark` varchar(128) DEFAULT NULL,
  `status` int NOT NULL,
  `dept_power` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `om_user_name_850a2498` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_user`
--

LOCK TABLES `om_user` WRITE;
/*!40000 ALTER TABLE `om_user` DISABLE KEYS */;
INSERT INTO `om_user` VALUES (1,'admin','2023-10-11 14:10:32.176322','sys','2023-10-18 19:41:32.606947','admin','gAAAAABlL8RseiGiK66-nty756_MZpBvTw9gar5_ADdmrBVpvDKeEM49nmwdtNrnpwhq03CQrQxO4OyhCdcnQ3T4UQ_A33-Bcf7kLN108hv30CiEyJxCY-A=','管理员',0,NULL,NULL,NULL,NULL,1,1),(2,'test001','2023-10-11 16:09:33.262068','sys','2023-10-13 17:54:54.279666','admin','gAAAAABmiMOmGhr_6SMdEljy1OahvH7acIu-Rn5r4dwiBnkOD0hgh21wbk16DwNNsG_et-4_tnEWyxnMD_gEb29wKvUVZtxCcQGJlqw_CJoe-pCMc3V4uXU=','测试',0,NULL,NULL,NULL,NULL,1,1);
/*!40000 ALTER TABLE `om_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `om_user_role`
--

DROP TABLE IF EXISTS `om_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `om_user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `om_user_role_name_1a0aa869` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `om_user_role`
--

LOCK TABLES `om_user_role` WRITE;
/*!40000 ALTER TABLE `om_user_role` DISABLE KEYS */;
INSERT INTO `om_user_role` VALUES (1,NULL,NULL,'2023-10-11 14:10:32.176322','2023-10-11 14:10:32.176322',NULL,1,1);
/*!40000 ALTER TABLE `om_user_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opstoken`
--

DROP TABLE IF EXISTS `opstoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `opstoken` (
  `token` varchar(128) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) DEFAULT NULL,
  `created_by` varchar(32) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(32) DEFAULT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  UNIQUE KEY `role_id` (`role_id`),
  CONSTRAINT `opstoken_role_id_fea8430a_fk_om_role_id` FOREIGN KEY (`role_id`) REFERENCES `om_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opstoken`
--

LOCK TABLES `opstoken` WRITE;
/*!40000 ALTER TABLE `opstoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `opstoken` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-11-23 15:42:32
