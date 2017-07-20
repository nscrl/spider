-- MySQL dump 10.15  Distrib 10.0.28-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: localhost
-- ------------------------------------------------------
-- Server version	10.0.28-MariaDB-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bdzd_master`
--

DROP TABLE IF EXISTS `bdzd_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bdzd_master` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `questionID` varchar(25) CHARACTER SET utf8 NOT NULL,
  `askTitle` varchar(50) CHARACTER SET utf8 NOT NULL,
  `qContent` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `askDate` date DEFAULT NULL,
  `answer` varchar(1000) CHARACTER SET utf8 DEFAULT NULL,
  `answerDate` date DEFAULT NULL,
  `good` int(11) DEFAULT NULL,
  `bad` smallint(6) DEFAULT NULL,
  `adoptRate` varchar(3) CHARACTER SET utf8 DEFAULT NULL,
  `answerType` char(1) DEFAULT '',
  `crawlDate` datetime DEFAULT NULL,
  `updateDate` datetime DEFAULT NULL,
  `cur_key` varchar(20) DEFAULT NULL,
  `cur_alias` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bdzd_minor`
--

DROP TABLE IF EXISTS `bdzd_minor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bdzd_minor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `questionID` varchar(25) CHARACTER SET utf8 NOT NULL,
  `othNo` smallint(6) DEFAULT NULL,
  `answer` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `othGood` smallint(6) DEFAULT NULL,
  `othBad` smallint(6) DEFAULT NULL,
  `answerDate` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-09 22:12:33
