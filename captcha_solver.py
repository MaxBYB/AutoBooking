import cv2
import ddddocr
import numpy as np
from collections import defaultdict


_detector = ddddocr.DdddOcr(det=True)
_ocr = ddddocr.DdddOcr()


def _norm_text(text):
	return (text or "").strip().replace(" ", "")


def _crop_to_png_bytes(crop):
	ok, buf = cv2.imencode(".png", crop)
	if not ok:
		return None
	return buf.tobytes()


def _top3_candidates_from_probability(crop_bytes):
	"""尝试使用 ddddocr 的概率输出拿到 top3（不同版本可能不支持）。"""
	results = []
	try:
		prob_res = _ocr.classification(crop_bytes, probability=True)
	except Exception:
		return results

	# 常见格式1: {'charsets': [...], 'probability': [...]} 
	if isinstance(prob_res, dict):
		charsets = prob_res.get("charsets")
		probs = prob_res.get("probability")
		if isinstance(charsets, list) and isinstance(probs, list) and len(charsets) == len(probs):
			pairs = []
			for ch, p in zip(charsets, probs):
				ch_n = _norm_text(ch)
				if not ch_n:
					continue
				try:
					pairs.append((ch_n, float(p)))
				except Exception:
					pairs.append((ch_n, 0.0))
			pairs.sort(key=lambda x: x[1], reverse=True)
			for ch, _ in pairs:
				if ch not in results:
					results.append(ch)
				if len(results) >= 3:
					break

		# 常见格式2: {'text': '字', 'confidence': 0.99}
		if not results:
			text = _norm_text(prob_res.get("text", ""))
			if text:
				results.append(text)

	return results


def _augmented_crops(crop):
	"""生成轻量增广图，作为概率不可用时的兜底。"""
	aug = [crop]
	try:
		gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
		_, th1 = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
		_, th2 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
		aug.extend([cv2.cvtColor(th1, cv2.COLOR_GRAY2BGR), cv2.cvtColor(th2, cv2.COLOR_GRAY2BGR)])
	except Exception:
		pass
	return aug


def _top3_text_candidates(crop, fast_mode=True):
	"""返回单个小图的 top3 文字候选。"""
	votes = defaultdict(float)

	# 先尝试 probability 模式
	crop_bytes = _crop_to_png_bytes(crop)
	if crop_bytes is not None:
		prob_candidates = _top3_candidates_from_probability(crop_bytes)
		for i, text in enumerate(prob_candidates):
			votes[text] += 3.0 - i

		# 快速模式下，概率输出足够时直接返回，避免额外多视图识别
		if fast_mode and len(prob_candidates) >= 2:
			return prob_candidates[:3]

		# 原图再识别一次，作为轻量补充
		try:
			text = _norm_text(_ocr.classification(crop_bytes))
			if text:
				votes[text] += 1.0
		except Exception:
			pass

		if fast_mode and votes:
			ordered = sorted(votes.items(), key=lambda x: x[1], reverse=True)
			return [x[0] for x in ordered[:3]]

	# 概率不可用时，做多视图识别投票
	for img in _augmented_crops(crop):
		b = _crop_to_png_bytes(img)
		if b is None:
			continue
		try:
			text = _norm_text(_ocr.classification(b))
			if text:
				votes[text] += 1.0
		except Exception:
			continue

	if not votes:
		return []

	ordered = sorted(votes.items(), key=lambda x: x[1], reverse=True)
	return [x[0] for x in ordered[:3]]


def get_ordered_click_points(png_bytes, target_text_list, fast_mode=True):
	"""
	输入:
		png_bytes: 一张 png 截图的 bytes
		target_text_list: 待识别文字列表，如 ["羽", "毛", "球"]

	输出:
		按 target_text_list 顺序返回坐标列表，格式 [(x, y), ...]
	"""
	if not png_bytes:
		raise ValueError("png_bytes 不能为空")
	if not isinstance(target_text_list, list) or len(target_text_list) == 0:
		raise ValueError("target_text_list 必须是非空列表")

	np_arr = np.frombuffer(png_bytes, np.uint8)
	img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
	if img is None:
		raise ValueError("无法解码图片，请确认输入是有效 png bytes")

	bboxes = _detector.detection(png_bytes)
	if not bboxes:
		raise ValueError("未检测到可识别目标")

	candidates = []
	for box in bboxes:
		x1, y1, x2, y2 = box
		crop = img[y1:y2, x1:x2]
		top3 = _top3_text_candidates(crop, fast_mode=fast_mode)
		if not top3:
			continue

		text = top3[0]
		cx = int((x1 + x2) / 2)
		cy = int((y1 + y2) / 2)
		candidates.append({"text": text, "alts": top3, "point": (cx, cy)})

	ordered_points = []
	used_idx = set()
	for target in target_text_list:
		t = _norm_text(str(target))
		hit_idx = None

		# 精确匹配优先
		for i, c in enumerate(candidates):
			if i in used_idx:
				continue
			if any(_norm_text(a) == t for a in c.get("alts", [c["text"]])):
				hit_idx = i
				break

		# 包含匹配兜底
		if hit_idx is None:
			for i, c in enumerate(candidates):
				if i in used_idx:
					continue
				alts = c.get("alts", [c["text"]])
				if any(t and (_norm_text(a) in t or t in _norm_text(a)) for a in alts):
					hit_idx = i
					break

		if hit_idx is None:
			raise ValueError(
				"未匹配到目标文字: %s, 候选结果: %s"
				% (t, [c.get("alts", [c["text"]]) for c in candidates])
			)

		used_idx.add(hit_idx)
		ordered_points.append(candidates[hit_idx]["point"])

	return ordered_points


def get_ordered_click_points_with_image_size(png_bytes, target_text_list, fast_mode=True):
	"""
	返回: (points, img_width, img_height)
	其中 points 为按目标顺序排列的坐标列表 [(x, y), ...]
	"""
	if not png_bytes:
		raise ValueError("png_bytes 不能为空")

	np_arr = np.frombuffer(png_bytes, np.uint8)
	img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
	if img is None:
		raise ValueError("无法解码图片，请确认输入是有效 png bytes")

	h, w = img.shape[:2]
	points = get_ordered_click_points(png_bytes, target_text_list, fast_mode=fast_mode)
	return points, w, h


if __name__ == "__main__":
	with open(r"C:\Users\18810\Desktop\test.png", "rb") as f:
		img_bytes = f.read()
    
	targets = ["界", "并", "果"]
	points = get_ordered_click_points(img_bytes, targets)
	print("targets:", targets)
	print("points:", points)
