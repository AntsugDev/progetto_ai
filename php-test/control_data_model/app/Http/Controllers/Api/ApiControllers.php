<?php

namespace App\Http\Controllers\Api;
use App\Utils\Utils;


class ApiControllers extends Controller{


public function __construct(Utils $utils){
$utils = new Utils();
}

    pubic function index(){

            $data = $this->utils->getData();
            return response()->json($data);


    }

}