-- MySQL dump 10.13  Distrib 8.4.10, for Linux (x86_64)
--
-- Host: localhost    Database: moonpilot_db
-- ------------------------------------------------------
-- Server version	8.4.10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'chaima','labbouzchaima@gmail.com','$2b$12$RdG95kOksWGDOqgRDzf4eOu3NbuXDCtHpljs7XWEBCn4Ww4gGN9by',1,'2026-07-19 18:32:22','2026-07-22 10:23:00');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `generations`
--

DROP TABLE IF EXISTS `generations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `figma_file_id` varchar(255) NOT NULL,
  `github_repo_url` text,
  `status` varchar(50) DEFAULT 'in_progress',
  `error_code` varchar(50) DEFAULT NULL,
  `error_message` text,
  `metrics` json DEFAULT NULL,
  `started_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `generations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `generations`
--

LOCK TABLES `generations` WRITE;
/*!40000 ALTER TABLE `generations` DISABLE KEYS */;
INSERT INTO `generations` VALUES (21,4,'anjenjefjrjfnfrj',NULL,'failed',NULL,'The Figma file ID is invalid. Please check it and try again',NULL,'2026-05-21 10:17:58',NULL),(22,4,'nchalayemchilyouuum',NULL,'failed',NULL,'The Figma file ID is invalid. Please check it and try again',NULL,'2026-05-21 10:23:27',NULL),(23,4,'1467487225381387818',NULL,'failed',NULL,'The Figma file ID is invalid. Please check it and try again',NULL,'2026-05-21 10:26:45',NULL),(24,4,'{{ $(\'Webhook\').item.json.body.figma_id }}','https://github.com/chaimalabbouz/figma-to-react-20260521-123032','success',NULL,NULL,NULL,'2026-05-21 10:31:21',NULL),(25,5,'rI804rMrtavpfl7PQkQlGB',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"duration_s\": 68.8, \"success_rate_pct\": 100}, \"planner\": {\"entities\": 5, \"duration_s\": 58.1}, \"pipeline\": {\"total_real_s\": 765.5, \"parallelism_gain_pct\": 18}}','2026-07-19 12:21:25','2026-07-19 06:21:15'),(26,6,'test-apres-migration',NULL,'SUCCESS',NULL,NULL,'{\"design\": {\"duration_s\": 448.4, \"pages_generated\": 10}, \"backend\": {\"duration_s\": 68.8, \"success_rate_pct\": 100}, \"planner\": {\"duration_s\": 100.8}, \"frontend\": {\"duration_s\": 317.1, \"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5, \"parallelism_gain_pct\": 33}}','2026-07-19 21:36:05','2026-07-19 17:36:06'),(27,6,'test-erreur-figma',NULL,'FAILURE',NULL,'Quota de l\'API Figma d´┐¢pass´┐¢. R´┐¢essayez dans une heure.','null','2026-07-19 22:08:10','2026-07-19 18:08:09'),(28,6,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 07:24:34','2026-07-20 03:24:34'),(29,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 07:27:48','2026-07-20 03:27:48'),(30,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 08:15:44','2026-07-20 04:15:44'),(31,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 08:29:07','2026-07-20 04:29:06'),(32,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 08:45:04','2026-07-20 04:45:03'),(33,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 08:52:53','2026-07-20 04:52:53'),(34,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 09:25:10','2026-07-20 05:25:09'),(35,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 09:25:40','2026-07-20 05:25:39'),(36,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 09:31:37','2026-07-20 05:31:36'),(37,2,'test-email-succes',NULL,'FALSE',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 09:32:29','2026-07-20 05:32:29'),(38,2,'test-email-succes',NULL,'SUCCESS',NULL,NULL,'{\"backend\": {\"success_rate_pct\": 100}, \"frontend\": {\"pages_bound\": 8}, \"pipeline\": {\"total_real_s\": 765.5}}','2026-07-20 09:34:00','2026-07-20 05:34:01'),(39,2,'test-email-error',NULL,'FAILED',NULL,'Rate limit exceeded','null','2026-07-20 10:15:02','2026-07-20 06:15:03'),(40,2,'test-email-error',NULL,'FAILED',NULL,'Rate limit exceeded','null','2026-07-20 10:21:44','2026-07-20 06:21:43'),(41,4,'wqPJhW1IGi3H85aAAgaUj8',NULL,'FAILURE',NULL,'├ëchec de la g├®n├®ration du design.','null','2026-07-20 11:02:51','2026-07-20 07:02:51');
/*!40000 ALTER TABLE `generations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `github_id` bigint NOT NULL,
  `github_login` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `github_id` (`github_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,999888,'test_user','newuser@example.com','Nouveau User','2026-05-19 15:53:30'),(2,555444,'test_email','labbouzchaima@gmail.com','chaima labbouz','2026-05-19 16:22:25'),(3,111333,'test_deux','labbouz@gmail.com','chima','2026-05-20 09:51:55'),(4,160781225,'chaimalabbouz','chaima.labbouz@etudiant-enit.utm.tn','Chaima Labbouz','2026-05-20 09:54:39'),(5,999999,'testuser','test@example.com','Test User','2026-07-18 22:54:30'),(6,888888,'testdocker','test@docker.com','Test Docker','2026-07-19 21:34:46');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-22 14:55:54
