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
    
    public function simulazione(){
    
    try{
    if(request()->validate([
        "costo_auto"=> "numeric|required",
        "k" => "numeric|required",
    ])){
        $data = request()->validationData();
        
        $ic = ($data['k']-1.3)/(1.6-1.3)
        $anticipo = 0.40*$ic*$data['costo_auto'];
        $finNuovaA =  $data['costo_auto']-$anticipo;
        
        return response()->json([
        "ic" => $ic,
        "anticipo" => $anticipo,
        "fin" =>$finNuovaA
        ]);
    
    }
    
    
    }catch(\Exception $e){
    
    echo $e->getMessage(); die;
    }
    
    
    }

}
