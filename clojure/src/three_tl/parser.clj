(ns three-tl.parser
  "3TL Parser - Parses 3TL files into Clojure data structures using Instaparse."
  (:require [instaparse.core :as insta]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.data.json :as json]))

;; Load the grammar from resources
(def grammar
  (insta/parser (io/resource "grammar.ebnf")))

;; Type conversion helpers
(defn parse-number [s]
  "Parse a string to a number (int or double)."
  (try
    (if (str/includes? s ".")
      (Double/parseDouble s)
      (Long/parseLong s))
    (catch Exception _ s)))

(defn parse-bool [s]
  "Parse boolean values."
  (case (str/lower-case s)
    "true" true
    "false" false
    s))

(defn clean-quoted-field [s]
  "Remove quotes and unescape doubled quotes from a quoted field."
  (-> s
      (str/replace #"^\"" "")
      (str/replace #"\"$" "")
      (str/replace #"\"\"" "\"")))

(defn clean-field-value [v]
  "Clean and convert field value to appropriate type."
  (cond
    (nil? v) nil
    (empty? v) nil
    :else
    (let [trimmed (str/trim v)]
      (cond
        (empty? trimmed) nil
        (= (str/lower-case trimmed) "null") nil
        (re-matches #"(?i)true|false" trimmed) (parse-bool trimmed)
        (re-matches #"-?\d+(\.\d+)?" trimmed) (parse-number trimmed)
        :else trimmed))))

;; Transform functions
(defn transform-type-modifier [modifiers]
  "Transform type modifiers (array, nullable)."
  (reduce
   (fn [acc modifier]
     (case (first modifier)
       :array-suffix (assoc acc :array? true)
       :nullable-suffix (assoc acc :nullable? true)
       acc))
   {:array? false :nullable? false}
   modifiers))

(defn extract-value [node]
  "Extract the value from a node (second element if it's a vector)."
  (if (vector? node)
    (second node)
    node))

(defn find-first [pred coll]
  "Find first element matching predicate."
  (first (filter pred coll)))

(defn transform-type [tree]
  "Transform a type expression into a type map."
  (let [base-type (atom nil)
        modifiers (atom [])
        params (atom nil)

        base-node (find-first #(and (vector? %) (= :base-type (first %))) tree)
        mod-node (find-first #(and (vector? %) (= :type-modifier (first %))) tree)]

    ;; Extract base type
    (when base-node
      (let [type-node (first (filter vector? (rest base-node)))]
        (when type-node
          (case (first type-node)
            :integer-type (reset! base-type (str/lower-case (second type-node)))
            :float-type (reset! base-type (str/lower-case (second type-node)))
            :bool-type (reset! base-type "bool")
            :text-type (reset! base-type (str/lower-case (second type-node)))
            :time-type (reset! base-type (str/lower-case (second type-node)))

            :decimal-type
            (let [precision-node (find-first #(and (vector? %) (= :precision (first %))) type-node)
                  scale-node (find-first #(and (vector? %) (= :scale (first %))) type-node)]
              (reset! base-type "decimal")
              (reset! params {:precision (parse-number (second precision-node))
                             :scale (parse-number (second scale-node))}))

            :ref-type
            (let [table-node (find-first #(and (vector? %) (= :ref-table (first %))) type-node)
                  column-node (find-first #(and (vector? %) (= :ref-column (first %))) type-node)
                  table-id (find-first #(and (vector? %) (= :identifier (first %))) table-node)
                  column-id (find-first #(and (vector? %) (= :identifier (first %))) column-node)]
              (reset! base-type "ref")
              (reset! params {:table (second table-id)
                             :column (second column-id)}))

            :enum-type
            (let [enum-vals-node (find-first #(and (vector? %) (= :enum-values (first %))) type-node)
                  id-nodes (filter #(and (vector? %) (= :identifier (first %))) enum-vals-node)]
              (reset! base-type "enum")
              (reset! params {:values (mapv second id-nodes)}))

            nil))))

    ;; Extract modifiers
    (when mod-node
      (doseq [child (rest mod-node)]
        (when (vector? child)
          (swap! modifiers conj child))))

    (merge
     {:base-type @base-type}
     (when @params {:params @params})
     (when (seq @modifiers) (transform-type-modifier @modifiers)))))

(defn format-type [type-map]
  "Format type map into a string representation."
  (let [{:keys [base-type params array? nullable?]} type-map
        type-str (cond
                   (= base-type "decimal")
                   (format "decimal(%s,%s)" (:precision params) (:scale params))

                   (= base-type "ref")
                   (format "ref(%s.%s)" (:table params) (:column params))

                   (= base-type "enum")
                   (format "enum(%s)" (str/join " | " (:values params)))

                   :else base-type)]
    (str type-str
         (when array? "[]")
         (when nullable? "?"))))

;; Main transformation
(defn transform-tree
  "Transform parse tree into Clojure data structures."
  [tree]
  (let [tables (atom [])]
    (clojure.walk/postwalk
     (fn [node]
       (if (and (vector? node) (keyword? (first node)))
         (case (first node)
           :three-tl-file (do
                           {:tables @tables})

           :table-block (let [table-name (atom nil)
                             columns (atom [])
                             rows (atom [])]
                         (doseq [child (rest node)]
                           (when (vector? child)
                             (case (first child)
                               :table-header
                               (let [id-node (first (filter #(and (vector? %) (= :identifier (first %))) child))]
                                 (reset! table-name (second id-node)))

                               :schema-def
                               (let [col-defs-node (first (filter #(and (vector? %) (= :col-defs (first %))) child))
                                     col-def-nodes (filter #(and (vector? %) (= :col-def (first %))) col-defs-node)]
                                 (reset! columns
                                        (mapv (fn [col-def]
                                               (let [col-name-node (first (filter #(and (vector? %) (= :identifier (first %))) col-def))
                                                     type-expr-node (first (filter #(and (vector? %) (= :type-expr (first %))) col-def))]
                                                 {:name (second col-name-node)
                                                  :type (format-type (transform-type type-expr-node))}))
                                             col-def-nodes)))

                               :data-row
                               (let [field-nodes (filter #(and (vector? %) (= :field (first %))) child)]
                                 (swap! rows conj
                                        (mapv (fn [field]
                                               (let [quoted (first (filter #(and (vector? %) (= :quoted-field (first %))) field))
                                                     unquoted (first (filter #(and (vector? %) (= :unquoted-field (first %))) field))
                                                     value (cond
                                                            quoted (clean-quoted-field (second quoted))
                                                            unquoted (second unquoted)
                                                            :else nil)]
                                                 (clean-field-value value)))
                                             field-nodes)))
                               nil)))
                         (swap! tables conj
                                {:name @table-name
                                 :columns @columns
                                 :rows @rows})
                         node)

           node)
         node))
     tree)
    {:tables @tables}))

;; Public API
(defn parse-string
  "Parse a 3TL string and return a data structure."
  [s]
  (let [result (grammar s)]
    (if (insta/failure? result)
      (throw (ex-info "Parse error" {:error (insta/get-failure result)}))
      (transform-tree result))))

(defn parse-file
  "Parse a 3TL file and return a data structure."
  [filepath]
  (parse-string (slurp filepath)))

(defn to-json
  "Convert parsed document to JSON string."
  ([doc] (to-json doc false))
  ([doc pretty?]
   (json/write-str doc :escape-slash false :indent (when pretty? 2))))

(defn -main
  "Main entry point for command-line usage."
  [& args]
  (if (empty? args)
    (do
      (println "Usage: clojure -M -m three-tl.parser <file.3tl> [--pretty]")
      (System/exit 1))
    (let [filepath (first args)
          pretty? (some #{"--pretty"} args)]
      (try
        (let [doc (parse-file filepath)]
          (println (to-json doc pretty?))
          (System/exit 0))
        (catch Exception e
          (binding [*out* *err*]
            (println "Error:" (.getMessage e)))
          (System/exit 1))))))
