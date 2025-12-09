CREATE TABLE `model_fe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reddito` decimal(10,3) NOT NULL,
  `altre_spese` decimal(10,3) NOT NULL,
  `request` decimal(10,3) NOT NULL,
  `taeg` decimal(10,3) DEFAULT NULL,
  `nr_rate` int DEFAULT NULL,
  `importo_rata` decimal(10,3) DEFAULT NULL,
  `sostenibilita` decimal(10,3) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `diff_reddito` decimal(10,3) DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `sync` char(1) DEFAULT 'S',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- finacial_estimated.model_versions definition

CREATE TABLE `model_versions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `version` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `n_rows` int DEFAULT NULL,
  `mae_rata` float DEFAULT NULL,
  `rmse_rata` float DEFAULT NULL,
  `r2_rata` float DEFAULT NULL,
  `mae_sost` float DEFAULT NULL,
  `rmse_sost` float DEFAULT NULL,
  `r2_sost` float DEFAULT NULL,
  `best_params` json DEFAULT NULL,
  `model_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- finacial_estimated.revisions definition

CREATE TABLE `revisions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nr_rata` int DEFAULT NULL,
  `importo_rata` float DEFAULT NULL,
  `sostenibilita` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- finacial_estimated.previsioning definition

CREATE TABLE `previsioning` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reddito` float DEFAULT NULL,
  `importo_fin` float DEFAULT NULL,
  `importo_rata` float DEFAULT NULL,
  `sostenibilita` float DEFAULT NULL,
  `decision` varchar(1024) DEFAULT NULL,
  `revision_id` int DEFAULT NULL,
  `is_accetable` char(1) DEFAULT 'N',
  PRIMARY KEY (`id`),
  KEY `fk_revision` (`revision_id`),
  CONSTRAINT `fk_revision` FOREIGN KEY (`revision_id`) REFERENCES `revisions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;