# Set directory
dir = 'D:\\Work&Education\\FakeNews'
setwd(dir)

#Read data
D201709 = read.csv("09-2017-news-forums-discussions.csv",stringsAsFactors = FALSE )
Data = data.frame(D201709[D201709$Type == "news",])
rm(D201709)
D201710 = read.csv("10-2017-news-forums-discussions.csv",stringsAsFactors = FALSE )
Data = data.frame(rbind(D201710[D201710$Type == "news",],Data))
rm(D201710)
D201711 = read.csv("11-2017-news-forums-discussions.csv",stringsAsFactors = FALSE )
Data = data.frame(rbind(D201711[D201711$Type == "news",],Data))
rm(D201711)

# Save data with news only
write.csv(Data,"Data.csv")
Data=read.csv("Data.csv",stringsAsFactors = FALSE)

# Edit data to get resource url 
str(Data)
Data$Resource_URL_Adj = gsub(".*\\.([^.]*\\.[^.]*)$", "\\1",
                           gsub("/.*$", "",
                                gsub("http://","",
                                     gsub("https://","", Data$resource_url))))


base::table(D201709[,"Type"])
URL = unique(Data$Resource_URL_Adj)
URL = data.frame(matrix(unlist(URL), byrow=T),stringsAsFactors=FALSE)
names(URL) = "URL"

# Get list of konspiratori URL
URL_konspiratori = read.csv("konspiratori.csv",stringsAsFactors = FALSE)

str(URL)
str(URL_konspiratori)
nrow(URL_konspiratori)
Data = merge(URL_konspiratori, URL, by = "URL")
nrow(Data)
# 25

# Get list of selected domains by traffic (netmonitor)
URL_relevant = data.frame(c("seznam.cz",
                 "idnes.cz",
                 "novinky.cz",
                 "blesk.cz",
                 "sport.cz",
                 "aktualne.cz",
                 "centrum.cz",
                 "denik.cz",
                 "ceskatelevize.cz",
                 "reflex.cz",
                 "extra.cz",
                 "penize.cz",
                 "eurozpravy.cz",
                 "lidovky.cz",
                 "ihned.cz",
                 "e15.cz",
                 "zive.cz",
                 "info.cz",
                 "finance.cz",
                 "euro.cz",
                 "tyden.cz",
                 "echo24.cz",
                 "livesport.cz",
                 "ceskenoviny.cz",
                 "respekt.cz",
                 "hlidacipes.org",
                  "irozhlas.cz",
                 "neovlivni.cz",
                 "tn.nova.cz",
                 "manipulatori.cz",
                 "tiscali.cz"
                 ))

# Clean and check URL penetration
names(URL_konspiratori) = "Resource_URL_Adj"
names(URL_relevant) = "Resource_URL_Adj" 
URL = rbind(URL_konspiratori,URL_relevant)
names(URL)

Data = merge(URL, Data, by = "Resource_URL_Adj")
nrow(Data)
names(Data)

names(URL_relevant) = "URL" 
merge(URL_konspiratori, URL_relevant, by = "URL")
merge(merge(URL, URL_relevant, by = "URL"),URL_konspiratori,by = "URL")
RELEVANT = merge(URL, URL_relevant, by = "URL")
table(URL_relevant$URL)
write.csv(RELEVANT,"URL_relevant.csv")

-------------------------------------------------------------------------------
# try to get Geneea data from json
install.packages("rjson")
library(rjson)

# Give the input file name to the function.
result <- fromJSON(file = "export.txt")
head(result)

json_file <- lapply(result, function(x) {
  x[sapply(x, is.null)] <- NA
  unlist(x)
})
json_file[[1]]
s = unlist(json_file, recursive = TRUE, use.names = TRUE)

head(a)
class(json_file)

json_file[1]

j<-unlist(json_file)

str(json_file)
class(json_file)

head(json_file)

library(stringr)
str_split_fixed(before$type, "_and_", 2)


json_file = do.call("rbind", json_file)
head(json_file)

str(result)
result$`geneea/sentiment`

# Create final data frame from json
df = data.frame(label = unlist(lapply(result,function(z) z$LABEL)),
               text=unlist(lapply(result,function(z) z$text)),
               #GeneeaTopics = paste(unlist(lapply(result$`geneea/topic`,function(z) z$label)),collapse=','),
               #GeneeaTopicsConf = paste(unlist(lapply(result,function(y) lapply(y$`geneea/topic`,function(z) z$confidence)),collapse=',')),
               #GeneeaTags = paste(unlist(lapply(result$`geneea/tags`,function(z) z$label)),collapse=','),
               Autor = unlist(lapply(result,function(z) z$author)),
               like_count = as.numeric(unlist(lapply(result,function(z) z$like_count))) ,
               Share_count = as.numeric(unlist(lapply(result,function(z) z$share_count))) ,                          
               Tags = unlist(lapply(result,function(z) z$tags)) , 
               #GeneeaSentiments = paste(unlist(lapply(s$`geneea/sentiment`,function(z) z$label)),collapse=','),  
               Resource_URL = unlist(lapply(result,function(z) z$resource_url)),
               date = unlist(lapply(result,function(z) z$date)), stringsAsFactors = FALSE
                 )

for(n in 1:nrow(df)){
  df[n,"sentiment"] <- paste(unlist(result[[n]]$`geneea/sentiment`),collapse=',')
}

for(n in 1:nrow(df)){
  df[n,"tags"] <- paste(unlist(result[[n]]$`geneea/tags`),collapse=',')
}

for(n in 1:nrow(df)){
  df[n,"topic"] <- paste(unlist(result[[n]]$`geneea/topic`),collapse=',')
}

df$Resource_URL_Adj = gsub(".*\\.([^.]*\\.[^.]*)$", "\\1",
                           gsub("/.*$", "",
                                gsub("http://","",
                                     gsub("https://","", df$Resource_URL))))
unique(df[,c("Resource_URL","Resource_URL_Adj")])

head(df[1,])

base::table(df[,c("Resource_URL","sentiment")])
tabS = data.frame(base::table(df[df$Resource_URL_Adj == "ceskatelevize.cz",c("Resource_URL","tags","sentiment")]))

### Topic analysis
head(df$topic)
DATA = df 
df$topic2 = as.character(gsub('([0-9]),','\\1;',df$topic))
head(df[1:4,])
str(df[,c("Resource_URL_Adj","topic2")])

dt= data.table(df[,c("Resource_URL_Adj","topic2")])
dt = dt[,.( Resource_URL_Adj
           # , topic2
            , topic2=unlist(strsplit(topic2, ";"))
),by=seq_len(nrow(dt))]
head(dt[1:4,])

library(stringr)
dt = cbind(dt,str_split_fixed(dt$topic2, ",", 2))
head(dt[1:10,])
names(dt) = c("seq_len","Resource_URL_Adj","topic2","topic","score")
head(dt)

-----------------------------------------------------------------------------
##### SHARED
names(Data)
base::table(Data$share_count)
head(Data)
SHARED_MEDIAN = data.frame(aggregate(share_count ~ Resource_URL_Adj, data = Data[Data$share_count > 0 & is.na(Data$share_count) == FALSE,], median))
names(SHARED_MEDIAN)

maxShared = max(SHARED_MEDIAN[SHARED_MEDIAN$Resource_URL_Adj != "procproto.cz","share_count"])*1.1
SHARED_MEDIAN$Shared_Rate = SHARED_MEDIAN$share_count/maxShared
names(SHARED_MEDIAN) = c( "Resource_URL_Adj", "share_count"  , "Shared_Rate" )
SHARED_MEDIAN[SHARED_MEDIAN$Resource_URL_Adj == "procproto.cz","Shared_Rate"] =1 
#URL_UNIQUE = data.frame(unique((Data$Resource_URL_Adj)))
#names(URL_UNIQUE) = "Resource_URL_Adj"
#SHARED = merge(URL_UNIQUE,SHARED_MEDIAN,by = "Resource_URL_Adj", all.x = TRUE)

SHARED[is.na(SHARED)] <- 0
head(SHARED)
names(SHARED) = c("Resource_URL_Adj", "share_count", "Shared_Rate" )
x <- toJSON(unname(split(SHARED[,c("Resource_URL_Adj", "share_count", "Shared_Rate")], 1:nrow(SHARED[,c("Resource_URL_Adj", "share_count", "Shared_Rate")]))))
print(cat(x))
write(x, "shared.json")
write.csv(SHARED,"SHARED.csv")

##### LIKES
names(URL_UR_COMP_DT) = c("label",    "Resource_URL_Adj" ,      "RU_MONTH",  "q" ,        "UP_80K")
names(URL_UR_COMP_DT)
head(URL_UR_COMP_DT)
DATA_RU = merge(URL_UR_COMP_DT,df,by = "Resource_URL_Adj",all.y = TRUE)

names(DATA_RU) = gsub(".x","",names(DATA_RU))
names(DATA_RU)
names(Data)
LIKE_MEDIAN = aggregate(like_count ~ Resource_URL_Adj, data = Data[Data$like_count > 0 & is.na(Data$like_count) == FALSE], median)

maxLike = max(LIKE_MEDIAN[LIKE_MEDIAN$Resource_URL_Adj != "procproto.cz","like_count"])*1.1
LIKE_MEDIAN$LikeRate = LIKE_MEDIAN$like_count/maxLike
names(LIKE_MEDIAN) = c( "Resource_URL_Adj", "like_count"  ,     "LikeRate" )
LIKE_MEDIAN[LIKE_MEDIAN$Resource_URL_Adj == "procproto.cz","LikeRate"] =1 
print(cat(x))
write(x, "like.json")










