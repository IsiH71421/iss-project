<?php
  $cb = file_get_contents('callback.url');
  $opts = array(
    'http'=>array(
      'method'=>"PUT",
      'header'=>"content-type: application/json\r\n",
      'content' => json_encode($_REQUEST)
    )
  );
  $context = stream_context_create($opts);
  $resp = file_get_contents($cb, false, $context); 
?>  
