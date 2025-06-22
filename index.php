<?php
  $requestUri = $_SERVER['REQUEST_URI'];

// Weiterleitung nur wenn exakt /iss/ oder /iss (ohne Dateinamen) aufgerufen wird
  if ($requestUri === '/~ge25fel/iss/' || $requestUri === '/~ge25fel/iss') {
    header("Location: display/index.html");
    exit;
  }
// sonst keine Weiterleitung, andere Seiten können geladen werden
?>