<?php

namespace App\Utils;

use App\Models\DataModel;
use Illuminate\Database\Eloquent\Collection;

class Utils
{
    private Collection $model;

    private float $max;

    private float $min;

    private float $avg;

    public function __construct()
    {
        $this->model = DataModel::all();
        $this->max = DataModel::max('diff_reddito');
        $this->min = DataModel::min('diff_reddito');
        $this->avg = DataModel::avg('diff_reddito');
    }

    public function getData()
    {
        try {
            $result = new \Illuminate\Support\Collection;
            $count = 1;
            $this->model->each(function ($item) use (&$result, &$count) {

                $importo = $this->getImport($item->costo_auto, !boolval($item->nuovo_usato));
                $rata = $this->getRata(intval($item->nr_rate), $importo, floatval($item->tan));
                $sostenibilita = $this->sostenibilita(floatval($item->diff_reddito), $rata);
                $coefficienteK = $this->coefficenteK($sostenibilita, $item->nr_rate);
                $Rincome = $this->RIncome(floatval($item->diff_reddito));
                $Ranticipo = $this->Ranticipo(!boolval($item->nuovo_usato), floatval($item->anticipo*100));
                $Re = $this->RE($Rincome,$Ranticipo);
                $Rs = $this->RS($sostenibilita);
                $Rd = $this->RD(!boolval($item->patentato), intval($item->nr_figli));
                $decisione = $this->score_decisionale($Re,$Rs,$Rd,$sostenibilita, !boolval($item->nuovo_usato),$coefficienteK,floatval($item->costo_auto), intval($item->nr_rate));
                $result->add([
                    'id' => $count,
                    'reddito'=>floatval($item->diff_reddito),
                    'Rincome' =>$Rincome,
                    'costo_auto'=>$item->costo_auto,
                    'formula'=> boolval($item->nuovo_usato) ? 'usata' :'nuova' ,
                    'anticipo'=>floatval($item->anticipo*100),
                    'Ranticipo'=> $Ranticipo,
                    'importo' => $importo,
                    'nrRate'=>$item->nr_rate,
                    'rata' => $rata,
                    'sostenibilita' => $sostenibilita,
                    'coefficienteK' => $coefficienteK,
                    'RE'=>$Re,
                    'RS'=>$Rs,
                    'RD'=> $Rd,
                    'Decisione_finale' => $decisione
                    
                ]);
                $count ++;
            });
			
			return $result;

        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }

    }

    public function getSoglia()
    {

        return $this->avg + ($this->avg * ($this->min / $this->max));
    }
    
    public function RIncome(float $reddito){
    
    $soglia = $this->getSoglia();
       if($reddito >= $soglia) 
        return 1;
       else if($reddito >= ($soglia *0.8))
       return 2;
        else if($reddito >= ($soglia *0.6))
       return 3;
         else if($reddito >= ($soglia *0.4))
       return 4;
       else return 5;
    }
    
    public function RE(int $Rincome, int $Ranticipo){
    
    $re =  (0.8*$Rincome)+(0.2*$Ranticipo);
    if($re <= 1.5 ) return 1;
    else if($re <= 1.5 ) return 1;
    else if($re <= 2.4 ) return 2;
    else if($re <= 3.2 ) return 3;
    else if($re <= 4 ) return 4;
    else return 5;
    
    }
    
    public function Ranticipo(bool $formula, float $anticipo){
    if(!$formula) return 1;
    else{
        if($anticipo >= 25) return 1;
        else if($anticipo >= 15 && $anticipo <=24) return 2;
        else if($anticipo >= 5 && $anticipo <=14) return 3;
        else return 4;
    }
    }
    
    public function RS(float $sostenibilita){
        if($sostenibilita <= 0.15) return 1;
        else if($sostenibilita >= 0.16 && $sostenibilita <= 0.20) return 2;
        else if($sostenibilita >= 0.21  && $sostenibilita <= 0.29) return 3;
        else if($sostenibilita >= 0.30 && $sostenibilita  <= 0.34) return 4;
        else return 5;
    
    }
    
    public function RD(bool $neoPatentati, int $nrFigli){
    $base = 0;
    if($nrFigli === 0) $base = 1;
    else if($nrFigli ===1) $base =2;
    else if($nrFigli ===2) $base =3;
    else $base= 4;
    
    if($neoPatentati) $base +=1;
    return $base;
    }
    
    public function score_decisionale(int $RE, int $RS, int $RD, float $sostenibilita, bool $formula, array $K, float $costoAuto, int $nrRate){
    
     $score = ($RE*0.5)+($RS*0.3)+($RD*0.2);
    if($sostenibilita >= 0.35) return "Non concedibile";
    else if($sostenibilita >= 0.21 && $sostenibilita <= 0.34 && !$formula){
        $importoDaAnticipare =array_key_exists(2,$K) && $K[2] >0 ?  $costoAuto *($K[2]/100) : 0;
        $nrRateT  = array_key_exists(3,$K) && $K[3] >0 ? $nrRate+$K[3] : $nrRate;
        return "Simulazione sceniario nuovo dove devo verificare e studiare se dando un anticipo di ".number_format($importoDaAnticipare,2,',','.')." euro, oppure aumentando le rate fino a $nrRateT cosa cambia ...";
    }else {
        if($score <= 1.5) return "Bonifico";
        else if($score >= 1.6 && $score < 4) return $formula ? 'Finanziamento a 3 anni' : 'Finanziamento Classico';
        else if($score >= 4 && $score < 5)  return 'Finanziamento con riserva (da simulare e dipendente da K)';
        else return "Non concedibile";
    }
    
   
    
    }
    
    
    public function getImport(float $reddito, bool $formula = true): float|int
    {
        if ($formula) {
            return $reddito * (10 / 100);
        } else {
            return $reddito;
        }

    }

    public function getRata(int $nrRate, float $importo, float $tan)
    {

        try {

            if ($nrRate > 0) {
                $tam = $tan / 12;

                $numeratore = $importo * $tam;
                $denominatore = 1 - ((1 + $tam) ** -$nrRate);
                if ($numeratore > 0 || $denominatore > 0) {
                    $rataMensile = $numeratore / $denominatore;

                    return $rataMensile;
                }
            }

            return 0;
        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }
    }

    public function sostenibilita(float $reddito, float $rata)
    {
        return $rata / $reddito;
    }

    public function coefficenteK(float $sostenibilita, int $nrRate)
    {
        if ($nrRate === 0) {
            return [0, 'Non calcolabile',0,0];
        }
        if ($sostenibilita <= 0.20) {
            return [1.0, 'Ottima'];
        } elseif ($sostenibilita >= 0.35) {
            return [round($sostenibilita / 0.20), 'Non concedibile',0,0];
        } else {
            $k = $sostenibilita / 0.20;
            //todo da rivedere o troppo alti i valori o troppo bassi
            $anticipo = round(($k - 1) * 80, 1);
            $nrRatePlus = intval(24 * ($k - 1));
            if ($k <= 1.20) {
                return [$k, "Azione: anticipo del $anticipo%", $anticipo, 0];
            } elseif ($k <= 1.40) {
                return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più", $anticipo, $nrRatePlus];
            } elseif ($k <= 1.70) {
                return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più",$anticipo, $nrRatePlus];
            } else {
                return [$k, 'Non sostenibile',0,0];
            }
        }
    }
}
