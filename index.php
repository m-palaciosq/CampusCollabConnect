<?php
$conn = new mysqli("localhost", "username", "password", "searchccc");

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 
echo "Connected successfully";
?>
