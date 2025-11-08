<?php

try{

    $host = '127.0.0.1';
    $db   = 'projectAI';
    $user = 'asugamele';
    $pass = '83Asugamele@';
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";

    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION, // Enable exceptions
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       // Fetch associative arrays
        PDO::ATTR_EMULATE_PREPARES   => false,                  // Use native prepared statements
    ];

    $pdo = new \PDO($dsn, $user, $pass, $options);
    if(!$pdo) throw new \Exception("Non sono connesso al db");
//echo "sono connesso ...";
    $query = $pdo->query("SELECT * FROM model_data")->fetchAll();
    $newData = [];
    array_walk($query,function($item, $key) use(&$newData){

        $importFinanziato = floatval($item["costo_auto"]);
        $rata = calcola_rata(floatval($item["costo_auto"]), !boolval($item["nuovo_usato"]), floatval($item["tan"]), intval($item["nr_rate"]),$importFinanziato);
        $sostenibilita = sotenibiita(floatval( $item["diff_reddito"]), floatval($rata));
        $cofficienteK = coefficienteK(floatval( $item["diff_reddito"]),$rata,$sostenibilita,intval($item["nr_rate"]));
        $punteggio = punteggio(floatval( $item["diff_reddito"]),$sostenibilita,
            floatval($item["anticipo"]),
            !boolval($item["nuovo_usato"]),
            !boolval($item["neo_patentato"]),
            intval($item["nr_figli"]), $cofficienteK
        );
        $newData[] = [
            "id" => $item["cliente"],
            "reddito_netto" => floatval($item["diff_reddito"]),
            "formula" => ($item["nuovo_usato"] === 0 ? 'Nuova' : 'Usata'),
            "costo_auto" => floatval($item["costo_auto"]),
            "importo_fin" => $importFinanziato,
            "tan" => (floatval($item["tan"])*100)."%",
            "nr_rate" => intval($item["nr_rate"]),
            "rata_mensile" => $rata,
            "sostenibilita" =>text_sostenibilità($sostenibilita),
            "coefficiente_k" => $cofficienteK,
            "punteggio" => $punteggio
        ];

    });

    echo json_encode($newData,true);



}catch(\Exception $e){
    var_dump($e);
    throw new \Exception($e->getMessage());
}

function text_sostenibilità(float $sostenibilita){

    $percent = floatval($sostenibilita *100);
    if($percent >= 25)
        return ["Rischioso", $percent."%"];
    else if($percent >=0 && $percent <= 15)
        return ["Alta sostenibilità",$percent."%"];
    else return ["Sostenibilità buona",$percent."%"];
}

function calcola_rata(float $costo,bool $formula,float $tan, int $nrRate,&$importoFin): int|float
{
    try{
        if($nrRate > 0){
            $tam = $tan / 12;
            $importoFin = $costo;
            if($formula)
                $importoFin = $costo *(10/100);

            $numeratore = $importoFin * $tam;
            $denominatore = 1-((1+$tam)**-$nrRate);
            if($numeratore === 0 || $denominatore === 0)
                die("importoFin=$importoFin;tam=$tam");
            if($denominatore === 0) return 0;
            $rataMensile = $numeratore / $denominatore;
            return $rataMensile;
        }
        return 0;

    }catch(\Exception $e){
        throw new \Exception($e->getMessage());
    }


}

function sotenibiita(float $reddito, float $rata): int|float
{
    return floatval($rata/$reddito);
}

function coefficienteK (float $reddito, float $rata, float $sostenibilita, int $nrRate): array
{

    if($nrRate === 0) return [0,"Non calcolabile"];
    if($sostenibilita <= 0.20) return [1.0,"Ottima"];
    else if($sostenibilita >= 0.35) return [round($sostenibilita/0.20), "Non concedibile"];
    else {
        $k = $sostenibilita /0.20;
        $anticipo = round(($k-1)*10,1);
        $nrRatePlus = intval(12*($k-1));
        if($k <= 1.20) return [$k, "Azione: anticipo del $anticipo%"];
        else if ($k <=1.40)return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più"];
        else if ($k <=1.70)return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più"];
        else return [$k, "Non sostenibile"];
    }
}

function punteggio(float $reddito, float $sotenibilita, float $anticipo, bool $formula,bool $neopatentati, int $nrFigli, array $cofficienteK) : array|string|int
{

    if($cofficienteK[0] === 0) return "Nessun interesse a calcolare";
    if($sotenibilita >= 0.35 || $cofficienteK[0] >= 1.70)
        return "Non concedibile";
    else if($sotenibilita <= 0.34){
        if($neopatentati)return "Finanziamento(".$cofficienteK[1].")";
        if($reddito <= 2500){
            if($nrFigli >=2)  return "Finanziamento (".$cofficienteK[1].")";
            else return $formula ? 'Finanziamento a 3 anni ('.$cofficienteK[1].')' : 'Finanziamento ('.$cofficienteK[1].')';
        }
        else {
            if($nrFigli >=2)  return "Bonifico";
            else{
                if($formula && $anticipo >= 0.25) return 'Finanziamento a 3 anni ('.$cofficienteK[1].')';
                else if(!$formula) return "Bonifico";
            }

        }



    }


}