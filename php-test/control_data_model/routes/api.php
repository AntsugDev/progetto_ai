<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ApiControllers;

Route::get('ctrl_test', [ApiControllers::class,'index']);
