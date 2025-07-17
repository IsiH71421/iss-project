<?php
  // Read the callback URL from a local file
  // This file should contain the endpoint URL where data will be forwarded
  $cb = file_get_contents('callback.url');

  // Configure HTTP request options for forwarding the data
  $opts = array(
    'http'=>array(
      'method'=>"PUT",                                    // Use PUT method for the request
      'header'=>"content-type: application/json\r\n",    // Set JSON content type header
      'content' => json_encode($_REQUEST)                 // Convert all incoming request data to JSON
    )
  );

  // Create HTTP context with the configured options
  $context = stream_context_create($opts);

  // Forward the request data to the callback URL and get the response
  $resp = file_get_contents($cb, false, $context);
?>
