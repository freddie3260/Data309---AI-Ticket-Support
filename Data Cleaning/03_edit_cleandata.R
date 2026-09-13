# library for R packages
source("Data Cleaning/00_library.R")

tickets <- read_excel("Data Cleaning/tickets_clean_400.xlsx")

# remove placeholder from clean data
# we do this because it have conflict with LLM and it cant identify the category of the ticket probably
tickets$body <- gsub("<[^>]+>", "", tickets$body)
tickets$body <- gsub("  +", " ", tickets$body)

tickets$answer <- gsub("<[^>]+>", "", tickets$answer)
tickets$answer <- gsub("  +", " ", tickets$answer)

write_xlsx(tickets, "Data Cleaning/tickets_clean_400_1.xlsx")
