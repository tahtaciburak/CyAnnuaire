# Docker Compose Files

To prepare big data environment of CyAnnuaire two docker compose files provided. It needs Apache Kafka for message passing, Elasticsearch for indexing and searching tweets and Kibana for visualizing statistics.

`docker-compose-kafka.yml` file runs a single node Apache Kafka with Zookeeper and Kafdrop. Kafdrop makes debugging and inspection easier while working with Kafka.

`docker-compose-elastic-kibana.yml` file runs 3 node elasticsearch cluster with single master node configuration. And also runs a Kibana for visualizing data inside elasticsearch.
