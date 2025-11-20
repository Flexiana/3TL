(ns three-tl.parser-test
  (:require [clojure.test :refer :all]
            [three-tl.parser :as parser]))

(deftest test-basic-table
  (testing "Parse a basic table"
    (let [content "#! User
#@ id:uint, name:str, email:str
1, Alice, alice@example.com
2, Bob, bob@example.com
"
          doc (parser/parse-string content)
          tables (:tables doc)]
      (is (= 1 (count tables)))
      (let [table (first tables)]
        (is (= "User" (:name table)))
        (is (= 3 (count (:columns table))))
        (is (= 2 (count (:rows table))))
        (is (= "id" (-> table :columns first :name)))
        (is (= "uint" (-> table :columns first :type)))
        (is (= 1 (-> table :rows first first)))
        (is (= "Alice" (-> table :rows first second)))))))

(deftest test-nullable-type
  (testing "Parse nullable types"
    (let [content "#! Article
#@ id:uint, title:str, content:str?
1, Hello, This is content
2, World,
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "str?" (-> table :columns (nth 2) :type)))
      (is (nil? (-> table :rows second (nth 2)))))))

(deftest test-array-type
  (testing "Parse array types"
    (let [content "#! Test
#@ id:uint, tags:str[]
1, tag1
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "str[]" (-> table :columns second :type))))))

(deftest test-decimal-type
  (testing "Parse decimal type"
    (let [content "#! Product
#@ id:uint, price:decimal(10,2)
1, 19.99
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "decimal(10,2)" (-> table :columns second :type)))
      (is (= 19.99 (-> table :rows first second))))))

(deftest test-ref-type
  (testing "Parse reference type"
    (let [content "#! Comment
#@ id:uint, article_id:ref(Article.id)
1, 42
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "ref(Article.id)" (-> table :columns second :type)))
      (is (= 42 (-> table :rows first second))))))

(deftest test-enum-type
  (testing "Parse enum type"
    (let [content "#! Task
#@ id:uint, status:enum(pending|in_progress|completed)
1, pending
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (re-find #"enum\(" (-> table :columns second :type)))
      (is (= "pending" (-> table :rows first second))))))

(deftest test-multiple-tables
  (testing "Parse multiple tables"
    (let [content "#! User
#@ id:uint, name:str
1, Alice

#! Post
#@ id:uint, user_id:ref(User.id), title:str
1, 1, My First Post
"
          doc (parser/parse-string content)
          tables (:tables doc)]
      (is (= 2 (count tables)))
      (is (= "User" (-> tables first :name)))
      (is (= "Post" (-> tables second :name)))
      (is (= 3 (-> tables second :columns count))))))

(deftest test-comments
  (testing "Comments are ignored"
    (let [content "# This is a comment
#! User
# Another comment
#@ id:uint, name:str
# Yet another comment
1, Alice
"
          doc (parser/parse-string content)
          tables (:tables doc)]
      (is (= 1 (count tables)))
      (is (= 1 (count (:rows (first tables))))))))

(deftest test-quoted-fields
  (testing "Parse quoted CSV fields"
    (let [content "#! Article
#@ id:uint, title:str, content:str
1, \"Hello, World\", \"This is a test\"
2, Normal, \"With \"\"quotes\"\" inside\"
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "Hello, World" (-> table :rows first second)))
      (is (= "This is a test" (-> table :rows first (nth 2))))
      (is (= "With \"quotes\" inside" (-> table :rows second (nth 2)))))))

(deftest test-case-insensitive-types
  (testing "Type names are case-insensitive"
    (let [content "#! Test
#@ id:UINT, name:STR, active:BOOL
1, Alice, true
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "uint" (-> table :columns first :type)))
      (is (= "str" (-> table :columns second :type)))
      (is (= "bool" (-> table :columns (nth 2) :type)))
      (is (true? (-> table :rows first (nth 2)))))))

(deftest test-unicode-identifiers
  (testing "Unicode in identifiers and data"
    (let [content "#! Café
#@ id:uint, nombre:str
1, José
"
          doc (parser/parse-string content)
          table (first (:tables doc))]
      (is (= "Café" (:name table)))
      (is (= "nombre" (-> table :columns second :name)))
      (is (= "José" (-> table :rows first second))))))

(deftest test-to-json
  (testing "JSON serialization"
    (let [content "#! User
#@ id:uint, name:str
1, Alice
"
          doc (parser/parse-string content)
          json-str (parser/to-json doc)]
      (is (string? json-str))
      (is (.contains json-str "User"))
      (is (.contains json-str "Alice"))
      (is (.contains json-str "tables")))))

