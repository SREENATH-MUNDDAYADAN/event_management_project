"""Phase 3: manual merge sort by event date."""
def merge_sort(items):
    if len(items)<=1: return items[:]
    mid=len(items)//2
    left=merge_sort(items[:mid]); right=merge_sort(items[mid:])
    out=[]; i=j=0
    while i<len(left) and j<len(right):
        if str(left[i]['event_date']) <= str(right[j]['event_date']): out.append(left[i]); i+=1
        else: out.append(right[j]); j+=1
    out.extend(left[i:]); out.extend(right[j:]); return out
