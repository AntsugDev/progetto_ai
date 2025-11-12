<?php

try {

    $host = '127.0.0.1';
    $db = 'projectAI';
    $user = 'asugamele';
    $pass = '83Asugamele@';
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";

    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, // Enable exceptions
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       // Fetch associative arrays
        PDO::ATTR_EMULATE_PREPARES => false,                  // Use native prepared statements
    ];

    $pdo = new \PDO($dsn, $user, $pass, $options);
    if (!$pdo) throw new \Exception("Non sono connesso al db");
    $query = $pdo->query("SELECT * FROM model_data")->fetchAll();

    $maxReddito = $pdo->query("SELECT MAX('diff_reddito') FROM model_data")->fetchColumn();
    $minReddito = $pdo->query("SELECT MINttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt('diff_reddito') FROM model_data")->fetchColumn();

} catch (\Exception $e) {
    die($e->getMessage());
}
