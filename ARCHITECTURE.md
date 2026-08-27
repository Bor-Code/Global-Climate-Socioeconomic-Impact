# Proje Mimarisi (Architecture)

Bu belge, **Global Climate & Socioeconomic Impact** projesinin veri boru hatlarını (data pipelines), orkestrasyonunu, API katmanını ve kullanıcı arayüzünü (Dashboard) tek bir kuşbakışı görünümle açıklar.

## Veri Akış Diyagramı (Data Flow Diagram)

Tüm sistem, veri kaynağından son kullanıcıya kadar tam otomatik bir zincir şeklinde kurgulanmıştır.

```mermaid
flowchart TD
    %% Veri Kaynakları
    subgraph Data Sources [Dış Veri Kaynakları (APIs)]
        WB[World Bank API <br> Ekonomik & Sosyal Veri]
        BE[Berkeley Earth <br> İklim & Sıcaklık]
    end

    %% Veri Çekme (Ingestion)
    subgraph Ingestion [Python + Polars Ingestion]
        Extract[generate_images.py <br> Veri Çekme ve Temizleme]
    end

    %% Veri Deposu
    subgraph Data Warehouse [DuckDB Veritabanı]
        DDB[(climate_wellbeing.duckdb <br> Merkezi Depo)]
    end

    %% Veri Dönüşümü
    subgraph Transformation [dbt Modelleri (SQL)]
        Staging[Staging Modelleri <br> stg_climate, stg_economy]
        Marts[Marts Modelleri <br> fct_climate_economy]
        Tests{Veri Kalitesi Testleri <br> Unique, Not Null, Range}
        
        Staging --> Marts
        Marts --> Tests
    end

    %% Orkestrasyon
    subgraph Orchestration [Dagster]
        DAG[Varlıklar (Assets) & Boru Hatları (Pipelines)]
    end

    %% Makine Öğrenimi
    subgraph Machine Learning [Scikit-Learn]
        ML[Random Forest Regressor <br> Mutluluk Skoru Tahmini]
        Model[(rf_model.pkl)]
        ML --> Model
    end

    %% Sunum Katmanı
    subgraph Presentation [Kullanıcı ve API Katmanı]
        Dash[Streamlit Dashboard <br> Veri Görselleştirme]
        Chatbot[Google Gemini API <br> SQL Data Agent]
        API[FastAPI <br> Mutluluk Tahmin Servisi]
        
        Chatbot --> Dash
    end

    %% Oklar / Akış
    WB --> Extract
    BE --> Extract
    Extract --> DDB
    
    DDB -.-> Transformation
    Transformation -.-> DDB
    
    DDB --> ML
    
    DDB --> Dash
    Model --> API
    
    DAG -.- Ingestion
    DAG -.- Transformation
    
    %% Stiller
    classDef source fill:#f9f,stroke:#333,stroke-width:2px;
    classDef db fill:#0f0,stroke:#333,stroke-width:2px;
    
    class WB,BE source;
    class DDB db;
```

## Altyapı ve Dağıtım (Infrastructure & Deployment)

Proje, kurumsal standartlarda **Docker Compose** kullanılarak konteynerleştirilmiş olup, **Terraform** aracılığıyla AWS üzerinde tek tuşla (Infrastructure as Code) ayağa kaldırılabilir.
Herhangi bir PR gönderildiğinde **GitHub Actions** ile kod standartları (`ruff`) ve birim testleri (`pytest`) otomatik olarak kontrol edilir.
