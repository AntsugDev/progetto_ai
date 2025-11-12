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
            $this->model->each(function ($item) use (&$result) {

                $importo = $this->getImport($item->costo_auto, ! boolval($item->nuovo_usato));
                $rata = $this->getRata(intval($item->nr_rate), $importo, floatval($item->tan));
                $sostenibilita = $this->sostenibilita(floatval($item->diff_reddito), $rata);
                $coefficienteK = $this->coefficenteK($sostenibilita, $item->nr_rate);
                $result->add([
                    'costo_auto'=>$item->costo_auto,
                    'formula'=> boolval($item->nuovo_usato) ? 'usata' :'nuova' ,
                    'importo' => $importo,
                    'rata' => $rata,
                    'sostenibilita' => $sostenibilita,
                    'coefficienteK' => $coefficienteK,
                ]);
            });

        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }

    }

    public function getSoglia(): float|int
    {

        return $this->avg + ($this->avg * ($this->min / $this->max));
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
            return [0, 'Non calcolabile'];
        }
        if ($sostenibilita <= 0.20) {
            return [1.0, 'Ottima'];
        } elseif ($sostenibilita >= 0.35) {
            return [round($sostenibilita / 0.20), 'Non concedibile'];
        } else {
            $k = $sostenibilita / 0.20;
            $anticipo = round(($k - 1) * 10, 1);
            $nrRatePlus = intval(12 * ($k - 1));
            if ($k <= 1.20) {
                return [$k, "Azione: anticipo del $anticipo%"];
            } elseif ($k <= 1.40) {
                return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più"];
            } elseif ($k <= 1.70) {
                return [$k, "Azione: anticipo del $anticipo% o $nrRatePlus rate in più"];
            } else {
                return [$k, 'Non sostenibile'];
            }
        }
    }
}