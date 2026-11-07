<?php
require 'auth.php';
if(isset($_GET['file'])){
    $include_url = basename($_GET['file']);
    $SANDBOX = getcwd() . "/uploads/";
    @include($SANDBOX . '/' . $include_url);
}