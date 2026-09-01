(ns achievement-validator.core
  (:require [ring.adapter.jetty :refer [run-jetty]]
            [cheshire.core :as json])
  (:gen-class))

;; Płynny spadek punktów
(defn dynamic-decay-multiplier [time-sec]
  (let [max-points 1000.0
        decay-rate 1.0
        min-points 50.0
        calculated (- max-points (* time-sec decay-rate))]
    (max min-points calculated)))

;; FUNKCJA WYŻSZEGO RZĘDU – przyjmuje tylko czas
(defn make-score-calculator [multiplier-fn]
  (fn [time-spent]
    (multiplier-fn time-spent)))

(defn check-speedrun-streak? [times-list]
  (loop [remaining times-list
         previous-time 999999]
    (if (empty? remaining)
      true
      (let [current-time (first remaining)]
        (if (> current-time previous-time)
          false
          (recur (rest remaining) current-time))))))

(defn process-player-data [data]
  (let [actions (:actions data)          ; Pobieramy WYŁĄCZNIE czasy akcji
        valid-actions (filter #(> % 0) actions)
        
        ;; Obliczamy wynik opierając się wyłącznie na czasie
        calculator (make-score-calculator dynamic-decay-multiplier)
        calculated-scores (map calculator valid-actions)
        
        total-score (reduce + 0 calculated-scores)
        is-speedrun (check-speedrun-streak? valid-actions)]
    
    {:total-score total-score
     :speedrun-achieved is-speedrun
     :status "processed_successfully"}))

(defn handler [request]
  (if (= (:request-method request) :post)
    (let [body-str (slurp (:body request))
          data (json/parse-string body-str true)
          result (process-player-data data)]
      
      ;; NOWOŚĆ: Wyświetlamy w konsoli OBLICZONY wynik, a nie surowe dane
      (println "Przeliczono punkty w Clojure:" result)
      
      {:status 200
       :headers {"Content-Type" "application/json"}
       :body (json/generate-string result)})
    {:status 405
     :headers {"Content-Type" "text/plain"}
     :body "Method Not Allowed"}))

(defn -main [& args]
  (println "Mikroserwis Clojure wystartował na porcie 8080...")
  (run-jetty handler {:port 8080}))