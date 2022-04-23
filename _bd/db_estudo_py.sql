-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 22, 2022 at 10:36 PM
-- Server version: 5.7.31
-- PHP Version: 7.1.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_estudo_py`
--

-- --------------------------------------------------------

--
-- Table structure for table `acesso`
--

DROP TABLE IF EXISTS `acesso`;
CREATE TABLE IF NOT EXISTS `acesso` (
  `codigo` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(80) NOT NULL,
  `senha` varchar(150) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `acesso`
--

INSERT INTO `acesso` (`codigo`, `login`, `senha`) VALUES
(1, 'admin@admin.com.br', '21232f297a57a5a743894a0e4a801fc3');

-- --------------------------------------------------------

--
-- Table structure for table `contato`
--

DROP TABLE IF EXISTS `contato`;
CREATE TABLE IF NOT EXISTS `contato` (
  `codigo` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `fone` varchar(14) NOT NULL,
  `cep` varchar(9) NOT NULL,
  `cidade` varchar(50) NOT NULL,
  `endereco` varchar(150) NOT NULL,
  `bairro` varchar(80) NOT NULL,
  `complemento` text NOT NULL,
  `dir_img` varchar(50) DEFAULT NULL,
  `nome_img` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `contato`
--

INSERT INTO `contato` (`codigo`, `nome`, `email`, `fone`, `cep`, `cidade`, `endereco`, `bairro`, `complemento`, `dir_img`, `nome_img`) VALUES
(1, 'Douglas Croti', 'douglascroti@gmail.com', '(99)12345-4321', '86701-565', 'Arapongas / PR', 'Rua Canário', 'Parque Veneza', 'Complemento App', '/static/imagens/', '20220422_223518.jpg');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
