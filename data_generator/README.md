## Data Generator

원래는 Graph API로 받아왔어야 할 지표 데이터를 random 생성하는 코드.
ex) 조회수, 릴스 재생 시간

* `reels.py` : 릴스 관련 지표 데이터를 생성
* `post.py` : 게시물 관련 지표 데이터를 생성
* `story.py` : 스토리 관련 지표 데이터를 생성

### How to use
```python
from data_generator import *

generate_reels_data()  # 릴스 하나에 대한 지표 데이터 생성
generate_post_data()  # 게시물 하나에 대한 지표 데이터 생성
generate_story_data()  # 스토리 하나에 대한 지표 데이터 생성
```