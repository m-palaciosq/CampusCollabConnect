<?php
$conn = new mysqli("localhost", "username", "password", "ccc");

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 
echo "Connected successfully";
?>
