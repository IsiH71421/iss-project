<?php
$cb = file_get_contents('callback.url');
$data = array("zoom" => "in");
$opts = array(
  'http'=>array(
    'method'=>"PUT",
    'header'=>"content-type: application/json\r\n",
    'content' => json_encode($data)
  )
);
$context = stream_context_create($opts);
$resp = file_get_contents($cb, false, $context);
?>