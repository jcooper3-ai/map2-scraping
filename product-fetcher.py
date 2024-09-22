import requests
import pandas as pd
# start timing the execution
import time

#Basically something that lets play with some dataset that has the embeddings. 
#Scaffolding to check if something's already in the database, and if it is if it's not. 

#Make the excel sheet, and then when I'm updating confirm that I'm not


def get_data(start_date, end_date):


    start_time = time.time()
    # Set the GraphQL endpoint and the headers
    endpoint = "https://www.producthunt.com/frontend/graphql"
    headers = {"Content-Type": "application/json"}

    # Define the GraphQL query and variables
    query = """
    query ArchivePage(
        $year: Int
        $month: Int
        $day: Int
        $cursor: String
        $order: PostsOrder
    ) {
        posts(
            first: 200
            year: $year
            month: $month
            day: $day
            order: $order
            after: $cursor
        ) {
            edges {
                node {
                    id
                    ...PostItemList
                    __typename
                }
                __typename
            }
            pageInfo {
                endCursor
                hasNextPage
                __typename
            }
            __typename
        }
    }
    fragment PostItemList on Post {
        id
        ...PostItem
        __typename
    }
    fragment PostItem on Post {
        id
        commentsCount
        name
        shortenedUrl
        slug
        tagline
        updatedAt
        pricingType
        topics(first: 1) {
            edges {
                node {
                    id
                    name
                    slug
                    __typename
                }
                __typename
            }
            __typename
        }
        redirectToProduct {
            id
            slug
            __typename
        }
        ...PostThumbnail
        ...PostVoteButton
        __typename
    }
    fragment PostThumbnail on Post {
        id
        name
        thumbnailImageUuid
        ...PostStatusIcons
        __typename
    }
    fragment PostStatusIcons on Post {
        id
        name
        productState
        __typename
    }
    fragment PostVoteButton on Post {
        id
        featuredAt
        updatedAt
        createdAt
        disabledWhenScheduled
        hasVoted
        ... on Votable {
            id
            votesCount
            __typename
        }
        __typename
    }
    """

    variables = {
        "year": 2022,
        "month": 12,
        "day": 13,
        "order": "DAILY_RANK",
        "cursor": None,
    }

    # Initialize an empty list to store the results
    results = []




    # get_date_range returns a list of dates between the start date and end date
    def get_date_range(start_date, end_date):
        from datetime import date, timedelta

        start_date = date(start_date["year"], start_date["month"], start_date["day"])
        end_date = date(end_date["year"], end_date["month"], end_date["day"])

        delta = end_date - start_date

        date_range = []
        for i in range(delta.days + 1):
            date_range.append(start_date + timedelta(days=i))

        return date_range


    for single_date in get_date_range(start_date, end_date):
        # Set the cursor to None and the hasNextPage flag to True
        cursor = None
        hasNextPage = True

        print(single_date.strftime("%Y-%m-%d"))
        # Fetch the products in a loop, until there are no more pages
        while hasNextPage:
            # update the date
            variables["year"] = single_date.year
            variables["month"] = single_date.month
            variables["day"] = single_date.day

            # Update the cursor in the variables
            variables["cursor"] = cursor

            # Set the GraphQL request payload
            payload = {"query": query, "variables": variables}

            # Send the POST request to the endpoint
            response = requests.post(endpoint, json=payload, headers=headers)

            # Check the status code of the response
            if response.status_code == 200:
                # Get the data from the response
                #print(response.json())
                data = response.json()["data"]


                # Extract the list of edges and pageInfo from the data
                edges = data["posts"]["edges"]
                pageInfo = data["posts"]["pageInfo"]

                # Extract the cursor and hasNextPage flag from the pageInfo
                cursor = pageInfo["endCursor"]
                hasNextPage = pageInfo["hasNextPage"]

                # Iterate over the edges and extract the node from each edge
                for edge in edges:
                    node = edge["node"]

                    # Extract the relevant fields from the node
                    id = node["id"]
                    name = node["name"]
                    slug = node["slug"]
                    tagline = node["tagline"]
                    shortenedUrl = node["shortenedUrl"]
                    commentsCount = node["commentsCount"]
                    updatedAt = node["updatedAt"]
                    pricingType = node["pricingType"]

                    # Extract the topic from the node, if it exists
                    topic = (
                        node["topics"]["edges"][0]["node"]
                        if node["topics"]["edges"]
                        else None
                    )
                    topic_id = topic["id"] if topic else None
                    topic_name = topic["name"] if topic else None
                    topic_slug = topic["slug"] if topic else None

                    # Extract the redirectToProduct from the node, if it exists
                    redirectToProduct = node["redirectToProduct"]
                    redirectToProduct_id = (
                        redirectToProduct["id"] if redirectToProduct else None
                    )
                    redirectToProduct_slug = (
                        redirectToProduct["slug"] if redirectToProduct else None
                    )

                    # Extract complete info from PostVoteButton and PostThumbnail
                    featuredAt = node["featuredAt"]
                    createdAt = node["createdAt"]
                    disabledWhenScheduled = node["disabledWhenScheduled"]
                    votesCount = node["votesCount"]
                    productState = node["productState"]
                    thumbnailImageUuid = node["thumbnailImageUuid"]

                    # Append the extracted fields to the results list
                    results.append(
                        {
                            "id": id,
                            "name": name,
                            "slug": slug,
                            "tagline": tagline,
                            "shortenedUrl": shortenedUrl,
                            "commentsCount": commentsCount,
                            "createdAt": createdAt,
                            "featuredAt": featuredAt,
                            "updatedAt": updatedAt,
                            "pricingType": pricingType,
                            "topic_id": topic_id,
                            "topic_name": topic_name,
                            "topic_slug": topic_slug,
                            "redirectToProduct_id": redirectToProduct_id,
                            "redirectToProduct_slug": redirectToProduct_slug,
                            "disabledWhenScheduled": disabledWhenScheduled,
                            "votesCount": votesCount,
                            "productState": productState,
                            "thumbnailImageUuid": thumbnailImageUuid,
                        }
                    )


    # Convert the results list to a Pandas DataFrame
    df = pd.DataFrame(results)

    # Write the DataFrame to a CSV file
    df.to_csv("products.csv", index=False)

    # end the timer
    end_time = time.time()

    # print the time taken to run the script
    print(f"Time taken to run the script: {end_time - start_time} seconds")
    return output_df
print('doing this')
output_df = get_data(start_date = {
        "year": 2024,
        "month": 9,
        "day": 11,
    }, end_date = {
        "year": 2024,
        "month": 9,
        "day": 21,
    })
output_df.to_csv("products.csv", index=False)

from datetime import datetime, timedelta
import os

def get_last_ten_days_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    return get_data(
        start_date={
            "year": start_date.year,
            "month": start_date.month,
            "day": start_date.day,
        },
        end_date={
            "year": end_date.year,
            "month": end_date.month,
            "day": end_date.day,
        }
    )

def merge_with_existing_db(filename, new_data):
    total_file = filename
    
    if os.path.exists(total_file):
        existing_df = pd.read_csv(total_file)
        merged_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=['id'], keep='last')
    else:
        merged_df = new_data
    
    merged_df.to_csv(total_file, index=False)
    print(f"Data merged and saved to {total_file}")

# Get data for the last 10 days
new_data = get_last_ten_days_data()

# Merge new data with existing database
filename = 'total.csv'
merge_with_existing_db(filename, new_data)



#Rn it assumes that historical data is there, and that there will only be new data from
#the past 10 days, and then it fetches those ten days and avoids duplicates. 
