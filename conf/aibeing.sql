/*
 Navicat Premium Data Transfer

 Source Server         : 是是是
 Source Server Type    : MySQL
 Source Server Version : 80033 (8.0.33)
 Source Host           : 127.0.0.1:3306
 Source Schema         : aibeing

 Target Server Type    : MySQL
 Target Server Version : 80033 (8.0.33)
 File Encoding         : 65001

 Date: 24/08/2023 16:59:45
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chat_history
-- ----------------------------
DROP TABLE IF EXISTS `chat_history`;
CREATE TABLE `chat_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_id` int DEFAULT NULL,
  `uid` varchar(100) DEFAULT NULL,
  `input` text,
  `output` text,
  `mp3` text,
  `emotion` varchar(100) DEFAULT NULL,
  `cost_time` int DEFAULT NULL,
  `cost` varchar(255) DEFAULT NULL,
  `like` tinyint DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for pure_chat
-- ----------------------------
DROP TABLE IF EXISTS `pure_chat`;
CREATE TABLE `pure_chat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(100) DEFAULT NULL,
  `input` text,
  `output` text,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for template
-- ----------------------------
DROP TABLE IF EXISTS `template`;
CREATE TABLE `template` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `avatar` varchar(100) DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `model` varchar(255) DEFAULT NULL,
  `token_cost_rate` float DEFAULT NULL,
  `voice_switch` tinyint(1) DEFAULT NULL,
  `voice_style` varchar(100) DEFAULT NULL,
  `voice_emotion` varchar(100) DEFAULT NULL,
  `vector_switch` tinyint(1) DEFAULT NULL,
  `vector_top_k` int DEFAULT NULL,
  `vector_collection` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `few_shot_switch` tinyint(1) DEFAULT NULL,
  `few_shot_content` text,
  `prompt` text,
  `character_prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
