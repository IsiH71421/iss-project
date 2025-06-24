<?php
  $headers = getallheaders();
  file_put_contents('callback.url',$headers['Cpee-Callback']);
  header('CPEE-CALLBACK: true');
  exit;
?>
