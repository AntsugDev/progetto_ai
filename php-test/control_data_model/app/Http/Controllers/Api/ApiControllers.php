<?php

namespace App\Http\Controllers\Api;
use App\Utils\Utils;
use App\Http\Controllers\Controller;


class ApiControllers extends Controller{




    public function index(){
            $utils = new Utils();
            $data = $utils->getData();
            $sogliaMinima = $utils->getSoglia();
            return response()->json([
            "soglia_reddito" => number_format($sogliaMinima,2,',','.'),
            "data_model"=>$data
            ]);


    }

}
