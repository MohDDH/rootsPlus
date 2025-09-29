SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `RootsPlusDatabase` DEFAULT CHARACTER SET utf8;
USE `RootsPlusDatabase`;

CREATE TABLE IF NOT EXISTS `User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NULL,
  `email` VARCHAR(50) NULL,
  `phone` VARCHAR(25) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Agronomist` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NULL,
  `email` VARCHAR(50) NULL,
  `phone` VARCHAR(25) NULL,
  `specialization` VARCHAR(60) NULL,
  `city` VARCHAR(50) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Farm` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `User_id` INT NOT NULL,
  `name` VARCHAR(60) NULL,
  `location` VARCHAR(100) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Farm_User_idx` (`User_id` ASC),
  CONSTRAINT `fk_Farm_User`
    FOREIGN KEY (`User_id`)
    REFERENCES `User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Crop` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Farm_id` INT NOT NULL,
  `crop_type` VARCHAR(60) NULL,
  `planting_date` DATETIME NULL,
  `area` FLOAT NULL,
  `status` VARCHAR(100) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Crop_Farm1_idx` (`Farm_id` ASC),
  CONSTRAINT `fk_Crop_Farm1`
    FOREIGN KEY (`Farm_id`)
    REFERENCES `Farm` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Activity` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Agronomist_id` INT NOT NULL,
  `Farm_id` INT NOT NULL,
  `Crop_id` INT NOT NULL,
  `activity_type` VARCHAR(60) NULL,
  `date` DATETIME NULL,
  `notes` TEXT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Activity_Agronomist1_idx` (`Agronomist_id` ASC),
  INDEX `fk_Activity_Farm1_idx` (`Farm_id` ASC),
  INDEX `fk_Activity_Crop1_idx` (`Crop_id` ASC),
  CONSTRAINT `fk_Activity_Agronomist1`
    FOREIGN KEY (`Agronomist_id`)
    REFERENCES `Agronomist` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Activity_Farm1`
    FOREIGN KEY (`Farm_id`)
    REFERENCES `Farm` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Activity_Crop1`
    FOREIGN KEY (`Crop_id`)
    REFERENCES `Crop` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Evaluation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Farm_id` INT NOT NULL,
  `Agronomist_id` INT NOT NULL,
  `season` VARCHAR(60) NULL,
  `yield_amount` FLOAT NULL,
  `activity_score` FLOAT NULL,
  `cost_efficiency` FLOAT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_Evaluation_Farm1_idx` (`Farm_id` ASC),
  INDEX `fk_Evaluation_Agronomist1_idx` (`Agronomist_id` ASC),
  CONSTRAINT `fk_Evaluation_Farm1`
    FOREIGN KEY (`Farm_id`)
    REFERENCES `Farm` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Evaluation_Agronomist1`
    FOREIGN KEY (`Agronomist_id`)
    REFERENCES `Agronomist` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Agronomist_has_Farm` (
  `Agronomist_id` INT NOT NULL,
  `Farm_id` INT NOT NULL,
  PRIMARY KEY (`Agronomist_id`, `Farm_id`),
  INDEX `fk_Agronomist_has_Farm_Farm1_idx` (`Farm_id` ASC),
  INDEX `fk_Agronomist_has_Farm_Agronomist1_idx` (`Agronomist_id` ASC),
  CONSTRAINT `fk_Agronomist_has_Farm_Agronomist1`
    FOREIGN KEY (`Agronomist_id`)
    REFERENCES `Agronomist` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Agronomist_has_Farm_Farm1`
    FOREIGN KEY (`Farm_id`)
    REFERENCES `Farm` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;