(defproject achievement-validator "0.1.0-SNAPSHOT"
  :description "Mikroserwis weryfikujący osiągnięcia w Clojure"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [ring/ring-core "1.9.6"]
                 [ring/ring-jetty-adapter "1.9.6"]
                 [cheshire "5.11.0"]]
  :main ^:skip-aot achievement-validator.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})