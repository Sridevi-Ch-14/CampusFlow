export type UserRole = 'STUDENT' | 'STAFF' | 'ADMIN' | 'SUPER_ADMIN';

export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ComplaintStatus =
  | 'OPEN'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'CLOSED'
  | 'REJECTED'
  | 'REOPENED';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  default_priority: Priority;
  is_active: boolean;
  created_at: string;
}

export interface RoomDetail {
  id: string;
  floor_id: string;
  room_number: string;
  room_type: string;
  floor_name?: string;
  building_name?: string;
  campus_name?: string;
  full_location_string?: string;
}

export interface Room {
  id: string;
  floor_id: string;
  room_number: string;
  room_type: string;
}

export interface Floor {
  id: string;
  building_id: string;
  floor_number: number;
  name: string;
  rooms: Room[];
}

export interface Building {
  id: string;
  campus_id: string;
  name: string;
  code: string;
  floors: Floor[];
}

export interface Campus {
  id: string;
  name: string;
  code: string;
  buildings: Building[];
}

export interface StatusHistory {
  id: string;
  previous_status?: ComplaintStatus;
  new_status: ComplaintStatus;
  changed_by: User;
  comment?: string;
  created_at: string;
}

export interface AssignmentHistory {
  id: string;
  staff: User;
  assigned_by: User;
  assigned_at: string;
  unassigned_at?: string;
  notes?: string;
}

export interface Comment {
  id: string;
  complaint_id: string;
  author: User;
  content: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  complaint_id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  storage_key: string;
  uploader: User;
  created_at: string;
  url: string;
}

export interface Rating {
  id: string;
  complaint_id: string;
  score: number;
  feedback?: string;
  student: User;
  created_at: string;
}

export interface Complaint {
  id: string;
  complaint_number: string;
  title: string;
  description: string;
  category: Category;
  location: RoomDetail;
  specific_location_details?: string;
  priority: Priority;
  status: ComplaintStatus;
  creator: User;
  assigned_staff?: User;
  sla_deadline: string;
  is_sla_breached: boolean;
  resolution_notes?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  closed_at?: string;

  status_history?: StatusHistory[];
  assignments?: AssignmentHistory[];
  comments?: Comment[];
  attachments?: Attachment[];
  rating?: Rating;
}

export interface ComplaintListItem {
  id: string;
  complaint_number: string;
  title: string;
  category: Category;
  location: RoomDetail;
  priority: Priority;
  status: ComplaintStatus;
  creator: User;
  assigned_staff?: User;
  sla_deadline: string;
  is_sla_breached: boolean;
  created_at: string;
  updated_at: string;
}

export interface ComplaintListResponse {
  items: ComplaintListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface NotificationItem {
  id: string;
  recipient_id: string;
  title: string;
  message: string;
  notification_type: string;
  reference_id?: string;
  is_read: boolean;
  created_at: string;
}

export interface AnalyticsKPI {
  total_complaints: number;
  open_complaints: number;
  assigned_complaints: number;
  in_progress_complaints: number;
  resolved_complaints: number;
  closed_complaints: number;
  rejected_complaints: number;
  sla_breached_complaints: number;
  avg_resolution_time_hours: number;
  resolution_rate_percent: number;
}

export interface AnalyticsDashboardData {
  kpi: AnalyticsKPI;
  by_category: { category_name: string; count: number }[];
  by_location: { building_name: string; count: number }[];
  by_priority: { priority: string; count: number }[];
  staff_workload: {
    staff_id: string;
    staff_name: string;
    assigned_count: number;
    in_progress_count: number;
    resolved_count: number;
  }[];
}
